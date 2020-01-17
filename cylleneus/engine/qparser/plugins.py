# Copyright 2011 Matt Chaput. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY MATT CHAPUT ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL MATT CHAPUT OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Matt Chaput.


from engine.qparser.syntax import *
import engine.query
import engine.query.positional
import whoosh.qparser
from engine.compat import u, xrange
from whoosh.qparser.taggers import FnTagger, RegexTagger



class WhitespacePlugin(whoosh.qparser.plugins.TaggingPlugin):
    """Tags whitespace and removes it at priority 500. Depending on whether
    your plugin's filter wants to see where whitespace was in the original
    query, it should run with priority lower than 500 (before removal of
    whitespace) or higher than 500 (after removal of whitespace).
    """

    nodetype = Whitespace
    priority = 100

    def __init__(self, expr=r"\s+"):
        whoosh.qparser.plugins.TaggingPlugin.__init__(self, expr)

    def filters(self, parser):
        return [(self.remove_whitespace, 500)]

    def remove_whitespace(self, parser, group):
        newgroup = group.empty_copy()
        for node in group:
            if isinstance(node, CylleneusGroupNode):
                newgroup.append(self.remove_whitespace(parser, node))
            elif not node.is_ws():
                newgroup.append(node)
        return newgroup


class SequencePlugin(whoosh.qparser.plugins.Plugin):
    """Adds the ability to group arbitrary queries inside double quotes to
    produce a query matching the individual sub-queries in sequence.
    """

    def __init__(self, expr='["](~(?P<slop>[1-9][0-9]*))?'):
        """
        :param expr: a regular expression for the marker at the start and end
            of a phrase. The default is the double-quotes character.
        """

        self.expr = expr

    class SequenceNode(CylleneusGroupNode):
        qclass = engine.query.positional.Sequence

    class QuoteNode(MarkerNode):
        def __init__(self, slop=None):
            self.slop = int(slop) if slop else 1

    def taggers(self, parser):
        return [(whoosh.qparser.taggers.FnTagger(self.expr, self.QuoteNode, "quote"), 0)]

    def filters(self, parser):
        return [(self.do_quotes, 499)]

    def do_quotes(self, parser, group):
        # New group to copy nodes into
        newgroup = group.empty_copy()
        # Buffer for sequence nodes; when it's None, it means we're not in
        # a sequence
        seq = None

        # Start copying nodes from group to newgroup. When we find a quote
        # node, start copying nodes into the buffer instead. When we find
        # the next (end) quote, put the buffered nodes into a SequenceNode
        # and add it to newgroup.
        for node in group:
            if isinstance(node, CylleneusGroupNode):
                # Recurse
                node = self.do_quotes(parser, node)

            if isinstance(node, self.QuoteNode):
                if seq is None:
                    # Start a new sequence
                    seq = []
                else:
                    # End the current sequence
                    sn = self.SequenceNode(seq, slop=node.slop)
                    newgroup.append(sn)
                    seq = None
            elif seq is None:
                # Not in a sequence, add directly
                newgroup.append(node)
            else:
                # In a sequence, add it to the buffer
                seq.append(node)

        # We can end up with buffered nodes if there was an unbalanced quote;
        # just add the buffered nodes directly to newgroup
        if seq is not None:
            newgroup.extend(seq)

        return newgroup


class PrefixPlugin(whoosh.qparser.plugins.TaggingPlugin):
    """Adds the ability to specify prefix queries by ending a term with an
    asterisk.
    This plugin is useful if you want the user to be able to create prefix but
    not wildcard queries (for performance reasons). If you are including the
    wildcard plugin, you should not include this plugin as well.
    >>> qp = qparser.QueryParser("content", myschema)
    >>> qp.remove_plugin_class(qparser.WildcardPlugin)
    >>> qp.add_plugin(qparser.PrefixPlugin())
    >>> q = qp.parse("pre*")
    """

    class PrefixNode(whoosh.qparser.syntax.TextNode):
        qclass = engine.query.terms.Prefix

        def r(self):
            return "%r*" % self.text

    expr = "(?P<text>[^ \t\r\n*]+)[*](?= |$|\\))"
    nodetype = PrefixNode


class WildcardPlugin(whoosh.qparser.plugins.TaggingPlugin):
    # \u055E = Armenian question mark
    # \u061F = Arabic question mark
    # \u1367 = Ethiopic question mark
    qmarks = u("?\u055E\u061F\u1367")
    expr = "(?P<text>[*%s])" % qmarks

    def filters(self, parser):
        # Run early, but definitely before multifield plugin
        return [(self.do_wildcards, 50)]

    def do_wildcards(self, parser, group):
        i = 0
        while i < len(group):
            node = group[i]
            if isinstance(node, self.WildcardNode):
                if i < len(group) - 1 and group[i + 1].is_text():
                    nextnode = group.pop(i + 1)
                    node.text += nextnode.text
                if i > 0 and group[i - 1].is_text():
                    prevnode = group.pop(i - 1)
                    node.text = prevnode.text + node.text
                else:
                    i += 1
            else:
                if isinstance(node, CylleneusGroupNode):
                    self.do_wildcards(parser, node)
                i += 1

        for i in xrange(len(group)):
            node = group[i]
            if isinstance(node, self.WildcardNode):
                text = node.text
                if len(text) > 1 and not any(qm in text for qm in self.qmarks):
                    if text.find("*") == len(text) - 1:
                        newnode = PrefixPlugin.PrefixNode(text[:-1])
                        newnode.startchar = node.startchar
                        newnode.endchar = node.endchar
                        group[i] = newnode
        return group

    class WildcardNode(whoosh.qparser.syntax.TextNode):
        # Note that this node inherits tokenize = False from TextNode,
        # so the text in this node will not be analyzed... just passed
        # straight to the query

        qclass = engine.query.terms.Wildcard

        def r(self):
            return "Wild %r" % self.text

    nodetype = WildcardNode


# ''
class FormPlugin(whoosh.qparser.plugins.TaggingPlugin):
    expr = r"('(?P<text>.*?)')"  # r"(^|(?<=\W))'(?P<text>.*?)'(?=\s|\]|[)}]|\"|$)"
    nodetype = FormNode

# <>
class LemmaPlugin(whoosh.qparser.plugins.TaggingPlugin):
    """Adds the ability to specify lemmas by enclosing them in guillemets."""

    expr = r'<(?P<text>[\w\d=:!@~#%msp|+-rc\/*>^$&<]+?)>'  # r'(^|(?<=\W))<(?P<text>[\w]+?)>(?=\s|\]|[)}]|:|"|$)'
    nodetype = LemmaNode

# []
class GlossPlugin(whoosh.qparser.plugins.TaggingPlugin):
    """Adds the ability to specify glosses by enclosing them in square brackets."""

    expr = r'\[(?P<text>[\w?#=!@~#%msp=|+-rc\/*>^$&<]+?)\]'  # r'(^|(?<=\W))\[(?P<text>[\w#]+?)\](?=\s|\]|[)}]|:|"|$)'
    nodetype = GlossNode

# {}
class SemfieldPlugin(whoosh.qparser.plugins.TaggingPlugin):
    """Adds the ability to specify semfields by enclosing them in curly brackets."""

    expr = r'{(?P<text>[\w\d ]+?)}'  # r'(^|(?<=\W)){(?P<text>[\w\d ]+?)}(?=\s|\]|[)}]|:|"|$)'
    nodetype = SemfieldNode


# //
class MorphosyntaxPlugin(whoosh.qparser.plugins.TaggingPlugin):
    """Adds the ability to specify morphosyntax queries by enclosing them in forward slashes."""

    expr = r'/(?P<text>[\w\d ]+?)/'  # r'(^|(?<=\W))/(?P<text>[\w\d ]+?)/(?=\s|\]|[)}]|:|"|$)'
    nodetype = MorphosyntaxNode


class RegexPlugin(whoosh.qparser.plugins.TaggingPlugin):
    """Adds the ability to specify regular expression term queries.

    The default syntax for a regular expression term is ``r"termexpr"``.

    >>> qp = qparser.QueryParser("content", myschema)
    >>> qp.add_plugin(qparser.RegexPlugin())
    >>> q = qp.parse('foo title:r"bar+"')
    """

    class RegexNode(whoosh.qparser.syntax.TextNode):
        qclass = whoosh.query.terms.Regex

        def r(self):
            return "Regex %r" % self.text

    expr = 'r"(?P<text>[^"]*)"'
    nodetype = RegexNode


class AnnotationPlugin(whoosh.qparser.plugins.TaggingPlugin):
    """Adds the ability to specify annotations for WordNet nodes following a colon."""

    expr = r":(?P<text>[A-Z0-9.]+)"
    nodetype = AnnotationNode


class AnnotationFilterPlugin(whoosh.qparser.plugins.TaggingPlugin):
    """Adds the ability to specify annotation filters for WordNet nodes following a colon."""

    expr = r"\|(?P<text>[A-Z0-9.]+)"
    nodetype = AnnotationFilterNode

    def filters(self, parser):
        return [(self.do_annotation, 490)]

    def do_annotation(self, parser, group):
        newgroup = group.empty_copy()
        for node in group:
            if isinstance(node, AnnotationFilterNode):
                if newgroup and newgroup[-1]:
                    # ignore annotation if the previous node is a FormNode
                    if isinstance(newgroup[-1], FormNode):
                        pass
                    elif isinstance(newgroup[-1], (LemmaNode, GlossNode, SemfieldNode)):
                        prev = newgroup.pop()
                        collocation = CollocationGroup()
                        collocation.extend([prev, node])
                        newgroup.append(collocation)
                    else:
                        newgroup.append(node)
                else:
                    newgroup.append(node)
            else:
                newgroup.append(node)
        return newgroup


class GroupPlugin(whoosh.qparser.plugins.Plugin):
    """Adds the ability to group clauses using parentheses.
    """

    # Marker nodes for open and close bracket

    class OpenBracket(CylleneusSyntaxNode):
        def r(self):
            return "("

    class CloseBracket(CylleneusSyntaxNode):
        def r(self):
            return ")"

    def __init__(self, openexpr="[(]", closeexpr="[)]"):
        self.openexpr = openexpr
        self.closeexpr = closeexpr

    def taggers(self, parser):
        return [(whoosh.qparser.taggers.FnTagger(self.openexpr, self.OpenBracket, "openB"), 0),
                (whoosh.qparser.taggers.FnTagger(self.closeexpr, self.CloseBracket, "closeB"), 0)]

    def filters(self, parser):
        return [(self.do_groups, 0)]

    def do_groups(self, parser, group):
        """This filter finds open and close bracket markers in a flat group
        and uses them to organize the nodes into a hierarchy.
        """

        ob, cb = self.OpenBracket, self.CloseBracket
        # Group hierarchy stack
        stack = [parser.group()]
        for node in group:
            if isinstance(node, ob):
                # Open bracket: push a new level of hierarchy on the stack
                stack.append(parser.group())
            elif isinstance(node, cb):
                # Close bracket: pop the current level of hierarchy and append
                # it to the previous level
                if len(stack) > 1:
                    last = stack.pop()
                    stack[-1].append(last)
            else:
                # Anything else: add it to the current level of hierarchy
                stack[-1].append(node)

        top = stack[0]
        # If the parens were unbalanced (more opens than closes), just take
        # whatever levels of hierarchy were left on the stack and tack them on
        # the end of the top-level
        if len(stack) > 1:
            for ls in stack[1:]:
                top.extend(ls)

        if len(top) == 1 and isinstance(top[0], CylleneusGroupNode):
            boost = top.boost
            top = top[0]
            top.boost = boost

        return top


class BoostPlugin(whoosh.qparser.plugins.TaggingPlugin):
    """Adds the ability to boost clauses of the query using the circumflex.
    """

    expr = "\\^(?P<boost>[0-9]*(\\.[0-9]+)?)($|(?=[ \t\r\n)\"]))"

    class BoostNode(CylleneusSyntaxNode):
        def __init__(self, original, boost):
            self.original = original
            self.boost = boost

        def r(self):
            return "^ %s" % self.boost

    def create(self, parser, match):
        # Override create so we can grab group 0
        original = match.group(0)
        try:
            boost = float(match.group("boost"))
        except ValueError:
            # The text after the ^ wasn't a valid number, so turn it into a
            # word
            node = FormNode(original)
        else:
            node = self.BoostNode(original, boost)

        return node

    def filters(self, parser):
        return [(self.clean_boost, 0), (self.do_boost, 510)]

    def clean_boost(self, parser, group):
        """This filter finds any BoostNodes in positions where they can't boost
        the previous node (e.g. at the very beginning, after whitespace, or
        after another BoostNode) and turns them into WordNodes.
        """

        bnode = self.BoostNode
        for i, node in enumerate(group):
            if isinstance(node, bnode):
                if (not i or not group[i - 1].has_boost):
                    group[i] = whoosh.qparser.syntax.to_word(node)
        return group

    def do_boost(self, parser, group):
        """This filter finds BoostNodes and applies the boost to the previous
        node.
        """

        newgroup = group.empty_copy()
        for node in group:
            if isinstance(node, CylleneusGroupNode):
                node = self.do_boost(parser, node)
            elif isinstance(node, self.BoostNode):
                if (newgroup and newgroup[-1].has_boost):
                    # Apply the BoostNode's boost to the previous node
                    newgroup[-1].set_boost(node.boost)
                    # Skip adding the BoostNode to the new group
                    continue
                else:
                    node = whoosh.qparser.syntax.to_word(node)
            newgroup.append(node)
        return newgroup


class OperatorsPlugin(whoosh.qparser.plugins.Plugin):
    """By default, adds the AND, OR, ANDNOT, ANDMAYBE, and NOT operators to
    the parser syntax. This plugin scans the token stream for subclasses of
    :class:`Operator` and calls their :meth:`Operator.make_group` methods
    to allow them to manipulate the stream.

    There are two levels of configuration available.

    The first level is to change the regular expressions of the default
    operators, using the ``And``, ``Or``, ``AndNot``, ``AndMaybe``, and/or
    ``Not`` keyword arguments. The keyword value can be a pattern string or
    a compiled expression, or None to remove the operator::

        qp = qparser.QueryParser("content", schema)
        cp = qparser.OperatorsPlugin(And="&", Or="\\|", AndNot="&!",
                                     AndMaybe="&~", Not=None)
        qp.replace_plugin(cp)

    You can also specify a list of ``(OpTagger, priority)`` pairs as the first
    argument to the initializer to use custom operators. See :ref:`custom-op`
    for more information on this.
    """

    class OpTagger(RegexTagger):
        def __init__(self, expr, grouptype, optype=whoosh.qparser.syntax.InfixOperator,
                     leftassoc=True, memo=""):
            RegexTagger.__init__(self, expr)
            self.grouptype = grouptype
            self.optype = optype
            self.leftassoc = leftassoc
            self.memo = memo

        def __repr__(self):
            return "<%s %r (%s)>" % (self.__class__.__name__,
                                     self.expr.pattern, self.memo)

        def create(self, parser, match):
            return self.optype(match.group(0), self.grouptype, self.leftassoc)

    def __init__(self, ops=None, clean=False,
                 And=r"(?<=\s)AND(?=\s)",
                 Or=r"(?<=\s)OR(?=\s)",
                 AndNot=r"(?<=\s)ANDNOT(?=\s)",
                 AndMaybe=r"(?<=\s)ANDMAYBE(?=\s)",
                 Not=r"(^|(?<=(\s|[()])))NOT(?=\s)",
                 Require=r"(^|(?<=\s))REQUIRE(?=\s)"):
        if ops:
            ops = list(ops)
        else:
            ops = []

        if not clean:
            ot = self.OpTagger
            if Not:
                ops.append((ot(Not, NotGroup, whoosh.qparser.syntax.PrefixOperator,
                               memo="not"), 0))
            if And:
                ops.append((ot(And, AndGroup, memo="and"), 0))
            if Or:
                ops.append((ot(Or, OrGroup, memo="or"), 0))
            if AndNot:
                ops.append((ot(AndNot, AndNotGroup,
                               memo="anot"), -5))
            if AndMaybe:
                ops.append((ot(AndMaybe, AndMaybeGroup,
                               memo="amaybe"), -5))
            if Require:
                ops.append((ot(Require, RequireGroup,
                               memo="req"), 0))

        self.ops = ops

    def taggers(self, parser):
        return self.ops

    def filters(self, parser):
        return [(self.do_operators, 600)]

    def do_operators(self, parser, group):
        """This filter finds PrefixOperator, PostfixOperator, and InfixOperator
        nodes in the tree and calls their logic to rearrange the nodes.
        """

        for tagger, _ in self.ops:
            # Get the operators created by the configured taggers
            optype = tagger.optype
            gtype = tagger.grouptype

            # Left-associative infix operators are replaced left-to-right, and
            # right-associative infix operators are replaced right-to-left.
            # Most of the work is done in the different implementations of
            # Operator.replace_self().
            if tagger.leftassoc:
                i = 0
                while i < len(group):
                    t = group[i]
                    if isinstance(t, optype) and t.grouptype is gtype:
                        i = t.replace_self(parser, group, i)
                    else:
                        i += 1
            else:
                i = len(group) - 1
                while i >= 0:
                    t = group[i]
                    if isinstance(t, optype):
                        i = t.replace_self(parser, group, i)
                    i -= 1

        # Descend into the groups and recursively call do_operators
        for i, t in enumerate(group):
            if isinstance(t, CylleneusGroupNode):
                group[i] = self.do_operators(parser, t)

        return group


#

class PlusMinusPlugin(whoosh.qparser.plugins.Plugin):
    """Adds the ability to use + and - in a flat OR query to specify required
    and prohibited terms.

    This is the basis for the parser configuration returned by
    ``SimpleParser()``.
    """

    # Marker nodes for + and -

    class Plus(whoosh.qparser.syntax.MarkerNode):
        pass

    class Minus(whoosh.qparser.syntax.MarkerNode):
        pass

    def __init__(self, plusexpr="\\+", minusexpr="-"):
        self.plusexpr = plusexpr
        self.minusexpr = minusexpr

    def taggers(self, parser):
        return [(FnTagger(self.plusexpr, self.Plus, "plus"), 0),
                (FnTagger(self.minusexpr, self.Minus, "minus"), 0)]

    def filters(self, parser):
        return [(self.do_plusminus, 510)]

    def do_plusminus(self, parser, group):
        """This filter sorts nodes in a flat group into "required", "optional",
        and "banned" subgroups based on the presence of plus and minus nodes.
        """

        required = AndGroup()
        optional = OrGroup()
        banned = OrGroup()

        # If the top-level group is an AndGroup we make everything "required" by default
        if isinstance(group, AndGroup):
            optional = AndGroup()

        # Which group to put the next node we see into
        next = optional
        for node in group:
            if isinstance(node, self.Plus):
                # +: put the next node in the required group
                next = required
            elif isinstance(node, self.Minus):
                # -: put the next node in the banned group
                next = banned
            else:
                # Anything else: put it in the appropriate group
                next.append(node)
                # Reset to putting things in the optional group by default
                next = optional

        group = optional
        if required:
            group = AndMaybeGroup([required, group])
        if banned:
            group = AndNotGroup([group, banned])
        return group


CollocationTagger = OperatorsPlugin.OpTagger(r"(?<=\s)WITH(?=\s)", CollocationGroup,
                                          whoosh.qparser.syntax.InfixOperator)
SequenceTagger = OperatorsPlugin.OpTagger(r"(?<=\s)THEN(?=\s)", SequenceGroup,
                                          whoosh.qparser.syntax.InfixOperator)
