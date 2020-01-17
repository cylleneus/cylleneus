from heapq import nlargest
from itertools import groupby

import cylleneus.engine.analysis
import cylleneus.engine.query
import cylleneus.engine.searching
from cylleneus import settings
import whoosh.highlight
from natsort import natsorted
from cylleneus.engine.compat import htmlescape


class CylleneusFragment(object):
    """Represents a fragment (extract) from a hit document. This object is
    mainly used to keep track of the start and end points of the fragment and
    the "matched" character ranges inside; it does not contain the text of the
    fragment or do much else.
    """

    def __init__(self, text, matches, startchar=0, endchar=-1, meta=None, start=None, end=None):
        """
        :param text: the source text of the fragment.
        :param matches: a list of objects which have ``startchar`` and
            ``endchar`` attributes, and optionally a ``text`` attribute.
        :param startchar: the index into ``text`` at which the fragment starts.
            The default is 0.
        :param endchar: the index into ``text`` at which the fragment ends.
            The default is -1, which is interpreted as the length of ``text``.
        """

        self.text = text
        self.matches = matches

        if endchar == -1:
            endchar = len(text)
        self.startchar = startchar
        self.endchar = endchar

        self.matched_terms = set()
        for t in matches:
            if hasattr(t, "text"):
                self.matched_terms.add((t.fieldname, t.text))

        self.meta = meta
        self.start = start
        self.end = end

    def __repr__(self):
        return "<Fragment %d:%d %d>" % (self.startchar, self.endchar,
                                        len(self.matches))

    def __len__(self):
        return self.endchar - self.startchar

    def same_divs(self, other):
        ssent = set()
        for match in self.matches:
            if 'sent_id' in match.meta:
                ssent.add(match.meta['sent_id'])
        osent = set()
        for match in other.matches:
            if 'sent_id' in match.meta:
                osent.add(match.meta['sent_id'])
        return any([sent in osent for sent in ssent])

    def is_adjacent(self, other):
        return (other.matches[0].pos - self.matches[-1].pos == 1) \
               and (other.matches[0].startchar - self.matches[-1].endchar == 1)

    def overlaps(self, fragment):
        if self.startchar == 0 and fragment.startchar == 0 \
            and self.endchar == 0 and fragment.endchar == 0:
            s = self.start
            e = self.end
            fs = fragment.start
            fe = fragment.end
            return (s <= fs <= e) or (s <= fe <= e)
        else:
            sc = self.startchar
            ec = self.endchar
            fsc = fragment.startchar
            fec = fragment.endchar
        return (sc <= fsc <= ec) or (sc <= fec <= ec)

    def overlapped_length(self, fragment):
        sc = self.startchar
        ec = self.endchar
        fsc = fragment.startchar
        fec = fragment.endchar
        return max(ec, fec) - min(sc, fsc)

    def __lt__(self, other):
        if hasattr(self.matches[0], 'meta'):
            divs = self.matches[0].meta['meta'].split('-')
            return tuple([v for k, v in self.matches[0].meta.items() if k in divs]) < tuple([v for k,
                                                                                                               v in
                                                                                                  other.matches[
                                                                                                      0].meta.items()
                                                                                                  if k in divs])
        else:
            return self.startchar < other.startchar

    def __eq__(self, other):
        if self.startchar == 0 and self.endchar == 0:
            return all([v == other.meta[k] for k, v in self.meta.items()])
        else:
            return self.startchar == other.startchar \
               and self.endchar == other.endchar \
               and self.text == other.text \
               and (self.pos == other.pos if hasattr(self, 'pos') else True)

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__)))


# Highlighting

def top_fragments(query, fragments, count, scorer, order, minscore=1):
    scored_fragments = ((scorer(query, f), f) for f in fragments)
    scored_fragments = nlargest(count, scored_fragments)
    best_fragments = [(score, fragment) for score, fragment in scored_fragments if score >= minscore]
    best_fragments.sort(key=lambda x: order(x[1]))
    return best_fragments


def highlight(text, terms, analyzer, fragmenter, formatter, top=3,
              scorer=None, minscore=1, order=whoosh.highlight.FIRST, mode="query"):

    if scorer is None:
        scorer = CylleneusBasicFragmentScorer()

    if type(fragmenter) is type:
        fragmenter = fragmenter()
    if type(formatter) is type:
        formatter = formatter()
    if type(scorer) is type:
        scorer = scorer()

    if scorer is None:
        scorer = CylleneusBasicFragmentScorer()

    termset = frozenset(terms)
    tokens = analyzer(text, chars=True, mode=mode, removestops=False)
    tokens = whoosh.highlight.set_matched_filter(tokens, termset)
    fragments = fragmenter.fragment_tokens(text, tokens)
    fragments = top_fragments(fragments, top, scorer, order, minscore)
    return formatter(text, fragments)


def get_boost(q, word):
    boost = 1
    for qt in q:
        if isinstance(qt,
                      (cylleneus.engine.query.compound.CylleneusCompoundQuery, cylleneus.engine.query.spans.SpanQuery)):
            boost = get_boost(qt, word)
        else:
            if word.split('::')[0] == qt.text.split('::')[0]:
                boost = qt.boost
        return boost

class CylleneusHighlighter(object):
    def __init__(self, fragmenter=None, scorer=None, formatter=None,
                 always_retokenize=False, order=whoosh.highlight.FIRST):
        self.fragmenter = fragmenter or whoosh.highlight.ContextFragmenter()
        self.scorer = scorer or CylleneusBasicFragmentScorer()
        self.formatter = formatter or CylleneusHtmlFormatter(tagname="b")
        self.order = order
        self.always_retokenize = always_retokenize

    def can_load_chars(self, results, fieldname):
        # Is it possible to build a mapping between the matched terms/docs and
        # their start and end chars for "pinpoint" highlighting (ie not require
        # re-tokenizing text)?

        if self.always_retokenize:
            # No, we've been configured to always retokenize some text
            return False
        if not results.has_matched_terms():
            # No, we don't know what the matched terms are yet
            return False
        if self.fragmenter.must_retokenize():
            # No, the configured fragmenter doesn't support it
            return False

        # Maybe, if the field was configured to store characters
        field = results.searcher.schema[fieldname]
        return field.supports("characters")

    @staticmethod
    def _load_chars(results, fieldname, texts, to_bytes):
        # For each docnum, create a mapping of text -> [(startchar, endchar)]
        # for the matched terms

        results._char_cache[fieldname] = cache = {}
        sorted_ids = sorted(docnum for _, docnum in results.top_n)

        for docnum in sorted_ids:
            cache[docnum] = {}

        for text in texts:
            btext = to_bytes(text)
            m = results.searcher.postings(fieldname, btext)
            docset = set(results.termdocs[(fieldname, btext)])
            for docnum in sorted_ids:
                if docnum in docset:
                    m.skip_to(docnum)
                    assert m.id() == docnum
                    cache[docnum][text] = m.value_as("characters")

    @staticmethod
    def _merge_matched_tokens(tokens):
        # Merges consecutive matched tokens together, so they are highlighted
        # as one

        token = None

        for t in tokens:
            if not t.matched:
                if token is not None:
                    yield token
                    token = None
                yield t
                continue
            if token is None:
                token = t.copy()
            elif t.chars and t.startchar <= token.endchar:
                if t.endchar > token.endchar:
                    token.text += t.text[token.endchar-t.endchar:]
                    token.endchar = t.endchar
            else:
                yield token
                token = None

        if token is not None:
            yield token

    def fragment_hit(self, hitobj, fieldname, text=None):
        results = hitobj.results
        schema = results.searcher.schema
        field = schema[fieldname]
        to_bytes = field.to_bytes
        from_bytes = field.from_bytes

        # Get the terms searched for/matched in this field
        if results.has_matched_terms():
            bterms = (term for term in results.matched_terms()
                      if term[0] == fieldname)
        else:
            bterms = results.query_terms(expand=True, fieldname=fieldname)

        # Convert bytes to unicode
        words = frozenset(from_bytes(term[1]) for term in bterms)

        # If we can do "pinpoint" highlighting...
        if self.can_load_chars(results, fieldname):
            # Build the docnum->[(startchar, endchar),] map
            if fieldname not in results._char_cache:
                self._load_chars(results, fieldname, words, to_bytes)  # fieldname
            hitterms = (from_bytes(term[1]) for term in hitobj.matched_terms()
                        if term[0] == fieldname)

            # Grab the word->[(startchar, endchar)] map for this docnum
            cmap = results._char_cache[fieldname][hitobj.docnum]

            # A list of Token objects for matched words
            tokens = []
            charlimit = self.fragmenter.charlimit
            for word in hitterms:
                chars = cmap[word]
                boost = None

                while boost is None:
                    boost = get_boost(hitobj.results.q, word)

                for pos, startchar, endchar, meta in chars:
                    if charlimit and endchar > charlimit:
                        break
                    t = cylleneus.engine.analysis.acore.CylleneusToken(docnum=hitobj['docix'], text=word, pos=pos,
                                                                       startchar=startchar, endchar=endchar,
                                                                       boost=boost,
                                                                       fieldname=field.__class__.__name__.lower())
                    t.meta = {item.split('=')[0]: item.split('=')[1] for item in meta[0]}
                    tokens.append(t)

            # Sort fragments by position in text, preferring standard references
            #   to char positions
            if hitobj.get('meta', False):
                # FIXME: some refs may be alphanumeric?
                tokens = natsorted(tokens,
                    key=lambda t: tuple(
                    [
                        v
                        for k, v in t.meta.items()
                        if k not in ['meta', 'sent_id']
                    ]))
            else:
                tokens = [max(group, key=lambda t: t.endchar - t.startchar)
                          for key, group in groupby(tokens, lambda t: t.startchar)]

            if text is None:
                if 'content' not in hitobj:
                    text = ''
                else:
                    text = hitobj['content']
            fragments = self.fragmenter.fragment_matches(text, tokens)
        else:
            # Retokenize the text
            analyzer = results.searcher.schema[fieldname].analyzer
            boost = hitobj.results.q.boost
            tokens = analyzer(text, positions=True, chars=True, mode="index",
                              removestops=False, boost=boost)
            # Set Token.matched attribute for tokens that match a query term
            tokens = whoosh.highlight.set_matched_filter(tokens, words)
            tokens = self._merge_matched_tokens(tokens)
            fragments = self.fragmenter.fragment_tokens(text, tokens)
        return fragments

    def highlight_hit(self, hitobj, fieldname, text=None, top=3, minscore=1):
        results = hitobj.results
        schema = results.searcher.schema
        field = schema[fieldname]
        to_bytes = field.to_bytes
        from_bytes = field.from_bytes

        if text is None:
            if fieldname not in hitobj:
                raise KeyError("Field %r is not stored." % fieldname)
            text = hitobj[fieldname]

        # Get the terms searched for/matched in this field
        if results.has_matched_terms():
            bterms = (term for term in results.matched_terms()
                      if term[0] == fieldname)
        else:
            bterms = results.query_terms(expand=True, fieldname=fieldname)
        # Convert bytes to unicode
        words = frozenset(from_bytes(term[1]) for term in bterms)

        # If we can do "pinpoint" highlighting...
        if self.can_load_chars(results, fieldname):
            # Build the docnum->[(startchar, endchar),] map
            if fieldname not in results._char_cache:
                self._load_chars(results, fieldname, words, to_bytes)

            hitterms = (from_bytes(term[1]) for term in hitobj.matched_terms()
                        if term[0] == fieldname)

            # Grab the word->[(startchar, endchar)] map for this docnum
            cmap = results._char_cache[fieldname][hitobj['docnum']]
            # A list of Token objects for matched words
            tokens = []
            charlimit = self.fragmenter.charlimit
            for word in hitterms:
                chars = cmap[word]
                for pos, startchar, endchar in chars:
                    if charlimit and endchar > charlimit:
                        break
                    tokens.append(
                        cylleneus.engine.analysis.acore.CylleneusToken(docnum=hitobj['docnum'], text=word, pos=pos,
                                                                       startchar=startchar, endchar=endchar))
            tokens.sort(key=lambda t: t.startchar)
            tokens = [max(group, key=lambda t: t.endchar - t.startchar)
                      for key, group in groupby(tokens, lambda t: t.startchar)]
            fragments = self.fragmenter.fragment_matches(text, tokens)
        else:
            # Retokenize the text
            analyzer = results.searcher.schema[fieldname].analyzer
            tokens = analyzer(text, positions=True, chars=True, mode="index",
                              removestops=False)
            # Set Token.matched attribute for tokens that match a query term
            tokens = whoosh.highlight.set_matched_filter(tokens, words)
            tokens = self._merge_matched_tokens(tokens)
            fragments = self.fragmenter.fragment_tokens(text, tokens)

        fragments = top_fragments(hitobj.results.q, fragments, top, self.scorer, self.order,
                                  minscore=minscore)
        output = self.formatter.format(fragments)
        return output


whoosh.highlight.Fragment = CylleneusFragment
whoosh.highlight.top_fragments = top_fragments


# Fragment scorers
class CylleneusBasicFragmentScorer(whoosh.highlight.FragmentScorer):
    def __call__(self, query, fragment):
        # if fragment.matches:
        #     if isinstance(query, (cylleneus.engine.query.positional.Sequence, whoosh.query.Sequence)):
        #         ordering = {
        #             (subq.fieldname, subq.text.split('::')[0]): q.pos
        #             for q in query
        #             for subq in q
        #             if hasattr(q, 'pos')
        #         }
        #     elif isinstance(query, (cylleneus.engine.query.compound.CylleneusCompoundQuery, whoosh.query.compound.CompoundQuery)):
        #         ordering = {
        #             (subq.fieldname, subq.text.split('::')[0]): 0
        #             for q in query
        #             for subq in q
        #         }
        #     else:
        #         ordering = {
        #             (q.fieldname, q.text.split('::')[0]): q.pos
        #             for q in query
        #             if hasattr(q, 'pos')
        #         }
        #
        #     # Add up the boosts for the matched terms in this passage
        #     boosted = set()
        #     score = 100
        #     if len(fragment.matched_terms) > 1:
        #         for t in fragment.matches:
        #             if t.text not in boosted:
        #                 score *= t.boost
        #                 boosted.add(t.text)
        #     else:
        #         score *= fragment.matches[0].boost
        #
        #     # Guarantee that sequential and compound queries get through
        #     if isinstance(query, cylleneus.engine.query.positional.Sequence):
        #         matches = sorted(fragment.matches, key=lambda m: m.startchar)
        #         for i, m in enumerate(matches):
        #             if i + 1 < len(matches):
        #                 o = matches[i+1]
        #                 if ordering[(o.fieldname, o.text.split('::')[0])] - ordering[(m.fieldname, m.text.split('::')[0])] != 1:
        #                     return 0
        #         if all(map(lambda m: (m.fieldname, m.text.split('::')[0]) in ordering, matches)):
        #             score *= 2
        #     elif isinstance(query, cylleneus.engine.query.compound.CylleneusCompoundQuery):
        #         matches = sorted(fragment.matches, key=lambda m: m.startchar)
        #         if all(map(lambda m: (m.fieldname, m.text.split('::')[0]) in query.iter_all_terms(), matches)):
        #             score *= 2
        #
        #     # Favor term diversity
        #     score *= (len(fragment.matched_terms) / cylleneus.engine.searching.total_terms(query)) or 1
        #
        #     # Require adjacency in sequential searches
        #     # Favor proximity in contextual searches, provided that the matched terms are different
        #     if len(fragment.matched_terms) > 1:
        #         if isinstance(query, cylleneus.engine.query.positional.Sequence):
        #             ordered = sorted(fragment.matches, key=lambda m: m.pos)
        #             for i, t in enumerate(ordered):
        #                 if i + 1 < len(fragment.matches):
        #                     if ordered[i+1].pos - t.pos != 1:
        #                         return 0
        #         elif isinstance(query, (cylleneus.engine.query.compound.CylleneusCompoundQuery,
        #                                 whoosh.query.compound.CompoundQuery)):
        #             dists = []
        #             matches = iter(sorted(fragment.matches, key=lambda t: t.pos))
        #             x = next(matches)
        #             while True:
        #                 try:
        #                     y = next(matches)
        #                 except StopIteration:
        #                     break
        #                 else:
        #                     if hasattr(x, 'pos') and hasattr(y, 'pos') and x.text != y.text:
        #                         if x.pos == 0 and y.pos == 0:  # ? to avoid div by zero
        #                             dists.append(-1)
        #                         else:
        #                             if x.fieldname != 'annotation' and y.fieldname != 'annotation':
        #                                 if ordering[(x.fieldname, x.text)] < ordering[(y.fieldname, y.text)]:
        #                                     dists.append(y.pos - x.pos)
        #                     x = y
        #             try:
        #                 m = statistics.mean(dists)
        #             except statistics.StatisticsError:
        #                 m = -1  # to avoid div by zero
        #             if m == 0:
        #                 m = 1
        #             if dists:
        #                 score *= (1 / m) * len(fragment.matches) / cylleneus.engine.searching.total_terms(query)
        #             else:
        #                 score *= len(fragment.matched_terms) / cylleneus.engine.searching.total_terms(query)
        # else:
        #     score = 0
        return cylleneus.engine.searching.total_terms(query) * 100


class CylleneusPinpointFragmenter(whoosh.highlight.Fragmenter):
    """This is a NON-RETOKENIZING fragmenter. It builds fragments from the
    positions of the matched terms.
    """

    def __init__(self, maxchars=settings.CHARS_OF_CONTEXT, surround=0, autotrim=False,
                 charlimit=whoosh.highlight.DEFAULT_CHARLIMIT):
        """
        :param maxchars: The maximum number of characters allowed in a
            fragment.
        :param surround: The number of extra characters of context to add both
            before the first matched term and after the last matched term.
        :param autotrim: automatically trims text before the first space and
            after the last space in the fragments, to try to avoid truncated
            words at the start and end. For short fragments or fragments with
            long runs between spaces this may give strange results.
        """

        self.maxchars = maxchars
        self.surround = surround
        self.autotrim = autotrim
        self.charlimit = charlimit

    def must_retokenize(self):
        return False

    def fragment_tokens(self, text, tokens):
        matched = [t for t in tokens if t.matched]
        return self.fragment_matches(text, matched)

    @staticmethod
    def _autotrim(fragment):
        text = fragment.text
        startchar = fragment.startchar
        endchar = fragment.endchar

        firstspace = text.find(" ", startchar, endchar)
        if firstspace > 0:
            startchar = firstspace + 1
        lastspace = text.rfind(" ", startchar, endchar)
        if lastspace > 0:
            endchar = lastspace

        if fragment.matches:
            startchar = min(startchar, fragment.matches[0].startchar)
            endchar = max(endchar, fragment.matches[-1].endchar)

        fragment.startchar = startchar
        fragment.endchar = endchar

    def fragment_matches(self, text, tokens):
        # For corpora without pinpoint support, return each token as a fragment
        if any([(token.pos == 0 and token.startchar == 0 and token.endchar == 0)
                for token in tokens]):
            for token in tokens:
                fragment = CylleneusFragment(text, [token,], meta=token.meta, start=0, end=0)
                yield fragment
        else:
            tokens = sorted(tokens, key=lambda t: t.startchar)

            maxchars = self.maxchars
            surround = self.surround
            autotrim = self.autotrim
            charlimit = self.charlimit

            j = -1

            for i, t in enumerate(tokens):
                if j >= i:
                    continue
                j = i
                left = t.startchar
                right = t.endchar
                if charlimit and right > charlimit:
                    break

                currentlen = right - left
                while j < len(tokens) - 1 and currentlen < maxchars:
                    next = tokens[j + 1]
                    ec = next.endchar
                    if ec - right <= surround and ec - left <= maxchars:
                        j += 1
                        right = ec
                        currentlen += (ec - next.startchar)
                    else:
                        break

                if text:
                    left = max(0, left - surround)
                    right = min(len(text), right + surround)

                fragment = CylleneusFragment(text, tokens[i:j + 1], left, right)
                if autotrim:
                    self._autotrim(fragment)
                yield fragment


def get_text(original, token, replace):
    """Convenience function for getting the text to use for a match when
    formatting.
    If ``replace`` is False, returns the part of ``original`` between
    ``token.startchar`` and ``token.endchar``. If ``replace`` is True, returns
    ``token.text``.
    """
    if replace:
        return token.text
    else:
        return original[token.startchar:token.endchar]


class CylleneusFormatter(object):
    """Base class for formatters.

    For highlighters that return strings, it is usually only necessary to
    override :meth:`Formatter.format_token`.

    Use the :func:`get_text` function as a convenience to get the token text::

        class MyFormatter(Formatter):
            def format_token(text, token, replace=False):
                ttext = get_text(text, token, replace)
                return "[%s]" % ttext
    """

    between = "\nEOF\n"

    def __init__(self, between="\nEOF\n"):
        """
        :param between: the text to add between fragments.
        """

        self.between = between

    def _text(self, text):
        return text

    def format_token(self, text, token, replace=False):
        """Returns a formatted version of the given "token" object, which
        should have at least ``startchar`` and ``endchar`` attributes, and
        a ``text`` attribute if ``replace`` is True.

        :param text: the original fragment text being highlighted.
        :param token: an object having ``startchar`` and ``endchar`` attributes
            and optionally a ``text`` attribute (if ``replace`` is True).
        :param replace: if True, the original text between the token's
            ``startchar`` and ``endchar`` indices will be replaced with the
            value of the token's ``text`` attribute.
        """

        raise NotImplementedError

    def format_fragment(self, fragment, replace=False):
        """Returns a formatted version of the given text, using the "token"
        objects in the given :class:`Fragment`, along with its meta data.

        :param fragment: a :class:`Fragment` object representing a list of
            matches in the text.
        :param replace: if True, the original text corresponding to each
            match will be replaced with the value of the token object's
            ``text`` attribute.
        """
        output = []
        index = fragment.startchar
        text = fragment.text

        for t in fragment.matches:
            if t.startchar is None:
                continue
            if t.startchar < index:
                continue
            if t.startchar > index:
                output.append(self._text(text[index:t.startchar]))
            output.append(self.format_token(text, t, replace))
            index = t.endchar
        output.append(self._text(text[index:fragment.endchar]))

        text = "".join(output)
        meta = fragment.meta if hasattr(fragment, 'meta') else None
        return meta, text

    def format(self, fragments, replace=False):
        """Returns a formatted version of the given text, using a list of
        :class:`Fragment` objects.
        """
        formatted = [self.format_fragment(f, replace=replace)
                     for s, f in fragments]
        return formatted

    def __call__(self, text, fragments):
        # For backwards compatibility
        return self.format(fragments)


class CylleneusDefaultFormatter(CylleneusFormatter):
    """Returns a string in which the matched terms are as given.
    """

    def format_token(self, text, token, replace=False):
        ttxt = get_text(text, token, replace)
        return ttxt


class CylleneusUppercaseFormatter(CylleneusFormatter):
    """Returns a string in which the matched terms are in UPPERCASE.
    """

    def format_token(self, text, token, replace=False):
        ttxt = get_text(text, token, replace)
        return ttxt.upper()


class CylleneusHtmlFormatter(CylleneusFormatter):
    """Returns a string containing HTML formatting around the matched terms.
    This formatter wraps matched terms in an HTML element with two class names.
    The first class name (set with the constructor argument ``classname``) is
    the same for each match. The second class name (set with the constructor
    argument ``termclass`` is different depending on which term matched. This
    allows you to give different formatting (for example, different background
    colors) to the different terms in the excerpt.
    >>> hf = HtmlFormatter(tagname="span", classname="match", termclass="term")
    >>> hf(mytext, myfragments)
    "The <span class="match term0">template</span> <span class="match term1">geometry</span> is..."
    This object maintains a dictionary mapping terms to HTML class names (e.g.
    ``term0`` and ``term1`` above), so that multiple excerpts will use the same
    class for the same term. If you want to re-use the same HtmlFormatter
    object with different searches, you should call HtmlFormatter.clear()
    between searches to clear the mapping.
    """

    template = '<%(tag)s class=%(q)s%(cls)s%(tn)s%(q)s>%(t)s</%(tag)s>'

    def __init__(self, tagname="strong", between="...",
                 classname="match", termclass="term", maxclasses=5,
                 attrquote='"'):
        """
        :param tagname: the tag to wrap around matching terms.
        :param between: the text to add between fragments.
        :param classname: the class name to add to the elements wrapped around
            matching terms.
        :param termclass: the class name prefix for the second class which is
            different for each matched term.
        :param maxclasses: the maximum number of term classes to produce. This
            limits the number of classes you have to define in CSS by recycling
            term class names. For example, if you set maxclasses to 3 and have
            5 terms, the 5 terms will use the CSS classes ``term0``, ``term1``,
            ``term2``, ``term0``, ``term1``.
        """

        self.between = between
        self.tagname = tagname
        self.classname = classname
        self.termclass = termclass
        self.attrquote = attrquote
        self.maxclasses = maxclasses
        self.seen = {}
        self.htmlclass = " ".join((self.classname, self.termclass))

    def _text(self, text):
        return htmlescape(text, quote=False)

    def format_token(self, text, token, replace=False):
        seen = self.seen
        ttext = self._text(get_text(text, token, replace))
        if ttext in seen:
            termnum = seen[ttext]
        else:
            termnum = len(seen) % self.maxclasses
            seen[ttext] = termnum

        return self.template % {"tag": self.tagname, "q": self.attrquote,
                                "cls": self.htmlclass, "t": ttext,
                                "tn": termnum}

    def clean(self):
        """Clears the dictionary mapping terms to HTML classnames.
        """
        self.seen = {}
