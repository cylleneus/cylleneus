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

import sys
import weakref

import cylleneus.engine.query.terms
import cylleneus.engine.query.spans
import cylleneus.engine.query.wrappers
import cylleneus.engine.query.positional
import cylleneus.engine.query.ranges
import cylleneus.engine.query.qcore
import cylleneus.engine.query.nested
import cylleneus.engine.query.compound
import whoosh.qparser.common
import whoosh.query
from whoosh.qparser import MarkerNode, TextNode, RegexPlugin
from whoosh.qparser.common import attach


class CylleneusSyntaxNode(object):
    """Base class for nodes that make up the abstract syntax tree (AST) of a
    parsed user query string. The AST is an intermediate step, generated
    from the query string, then converted into a :class:`whoosh.query.Query`
    tree by calling the ``query()`` method on the nodes.
    Instances have the following required attributes:
    ``has_fieldname``
        True if this node has a ``fieldname`` attribute.
    ``has_text``
        True if this node has a ``text`` attribute
    ``has_boost``
        True if this node has a ``boost`` attribute.
    ``startchar``
        The character position in the original text at which this node started.
    ``endchar``
        The character position in the original text at which this node ended.
    """

    has_fieldname = False
    has_text = False
    has_boost = False
    _parent = None

    def __repr__(self):
        r = "<"
        if self.has_fieldname:
            r += "%r:" % self.fieldname
        r += self.r()
        if self.has_boost and self.boost != 1.0:
            r += " ^%s" % self.boost
        r += ">"
        return r

    def r(self):
        """Returns a basic representation of this node. The base class's
        ``__repr__`` method calls this, then does the extra busy work of adding
        fieldname and boost where appropriate.
        """

        return "%s %r" % (self.__class__.__name__, self.__dict__)

    def apply(self, fn):
        return self

    def accept(self, fn):
        def fn_wrapper(n):
            return fn(n.apply(fn_wrapper))

        return fn_wrapper(self)

    def query(self, parser):
        """Returns a :class:`whoosh.query.Query` instance corresponding to this
        syntax tree node.
        """

        raise NotImplementedError(self.__class__.__name__)

    def is_ws(self):
        """Returns True if this node is ignorable whitespace.
        """

        return False

    def is_text(self):
        return False

    def set_fieldname(self, name, override=False):
        """Sets the fieldname associated with this node. If ``override`` is
        False (the default), the fieldname will only be replaced if this node
        does not already have a fieldname set.
        For nodes that don't have a fieldname, this is a no-op.
        """

        if not self.has_fieldname:
            return

        if self.fieldname is None or override:
            self.fieldname = name
        return self

    def set_boost(self, boost):
        """Sets the boost associated with this node.
        For nodes that don't have a boost, this is a no-op.
        """

        if not self.has_boost:
            return
        self.boost = boost
        return self

    def set_range(self, startchar, endchar):
        """Sets the character range associated with this node.
        """

        self.startchar = startchar
        self.endchar = endchar
        return self

    # Navigation methods

    def parent(self):
        if self._parent:
            return self._parent()

    def next_sibling(self):
        p = self.parent()
        if p:
            return p.node_after(self)

    def prev_sibling(self):
        p = self.parent()
        if p:
            return p.node_before(self)

    def bake(self, parent):
        self._parent = weakref.ref(parent)



class CylleneusGroupNode(CylleneusSyntaxNode):
    """Base class for abstract syntax tree node types that group together
    sub-nodes.
    Instances have the following attributes:
    ``merging``
        True if side-by-side instances of this group can be merged into a
        single group.
    ``qclass``
        If a subclass doesn't override ``query()``, the base class will simply
        wrap this class around the queries returned by the subnodes.
    This class implements a number of list methods for operating on the
    subnodes.
    """

    has_boost = True
    has_annotation = True
    merging = True
    qclass = None

    def __init__(self, nodes=None, boost=1.0, annotation=None, **kwargs):
        self.nodes = nodes or []
        self.boost = boost
        self.annotation = annotation
        self.kwargs = kwargs

    def r(self):
        return "%s %s" % (self.__class__.__name__,
                          ", ".join(repr(n) for n in self.nodes))

    @property
    def startchar(self):
        if not self.nodes:
            return None
        return self.nodes[0].startchar

    @property
    def endchar(self):
        if not self.nodes:
            return None
        return self.nodes[-1].endchar

    def apply(self, fn):
        return self.__class__(self.type, [fn(node) for node in self.nodes],
                              boost=self.boost, **self.kwargs)

    def query(self, parser):
        subs = []
        for node in self.nodes:
            subq = node.query(parser)

            if subq is not None:
                subs.append(subq)

        q = self.qclass(subs, boost=self.boost, **self.kwargs)
        return attach(q, self)

    def empty_copy(self):
        """Returns an empty copy of this group.
        This is used in the common pattern where a filter creates an new
        group and then adds nodes from the input group to it if they meet
        certain criteria, then returns the new group::
            def remove_whitespace(parser, group):
                newgroup = group.empty_copy()
                for node in group:
                    if not node.is_ws():
                        newgroup.append(node)
                return newgroup
        """

        c = self.__class__(**self.kwargs)
        if self.has_boost:
            c.boost = self.boost
        if self.has_fieldname:
            c.fieldname = self.fieldname
        if self.has_text:
            c.text = self.text
        if self.annotation:
            c.annotation = self.annotation
        return c

    def set_fieldname(self, name, override=False):
        CylleneusSyntaxNode.set_fieldname(self, name, override=override)
        for node in self.nodes:
            node.set_fieldname(name, override=override)

    def set_range(self, startchar, endchar):
        for node in self.nodes:
            node.set_range(startchar, endchar)
        return self

    # List-like methods

    def __nonzero__(self):
        return bool(self.nodes)

    __bool__ = __nonzero__

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)

    def __getitem__(self, n):
        return self.nodes.__getitem__(n)

    def __setitem__(self, n, v):
        self.nodes.__setitem__(n, v)

    def __delitem__(self, n):
        self.nodes.__delitem__(n)

    def insert(self, n, v):
        self.nodes.insert(n, v)

    def append(self, v):
        self.nodes.append(v)

    def extend(self, vs):
        self.nodes.extend(vs)

    def pop(self, *args, **kwargs):
        return self.nodes.pop(*args, **kwargs)

    def reverse(self):
        self.nodes.reverse()

    def index(self, v):
        return self.nodes.index(v)

    # Navigation methods

    def bake(self, parent):
        CylleneusSyntaxNode.bake(self, parent)
        for node in self.nodes:
            node.bake(self)

    def node_before(self, n):
        try:
            i = self.nodes.index(n)
        except ValueError:
            return
        if i > 0:
            return self.nodes[i - 1]

    def node_after(self, n):
        try:
            i = self.nodes.index(n)
        except ValueError:
            return
        if i < len(self.nodes) - 2:
            return self.nodes[i + 1]


class AndGroup(CylleneusGroupNode):
    qclass = cylleneus.engine.query.compound.And


class OrGroup(CylleneusGroupNode):
    qclass = cylleneus.engine.query.compound.Or

    @classmethod
    def factory(cls, scale=1.0):
        def maker(nodes=None, **kwargs):
            return cls(nodes=nodes, scale=scale, **kwargs)
        return maker


class WordNetNode(TextNode):
    annotation = None

    def query(self, parser):
        fieldname = self.fieldname or parser.fieldname
        termclass = self.qclass or parser.termclass
        q = parser.term_query(fieldname, self.text, termclass,
                              boost=self.boost, tokenize=self.tokenize,
                              removestops=self.removestops, annotation=self.annotation)

        return whoosh.qparser.common.attach(q, self)


class FormNode(WordNetNode):
    qclass = cylleneus.engine.query.terms.Form
    tokenize = False
    removestops = False

    def __init__(self, text):
        self.fieldname = 'form'
        self.text = text
        self.boost = 1.0

    def __repr__(self):
        r = "<"
        if self.has_fieldname:
            r += "%r:" % self.fieldname
        r += f"'{self.text}'"
        if self.has_boost and self.boost != 1.0:
            r += " ^%s" % self.boost
        r += ">"
        return r

    def r(self):
        return "%s %r" % (self.__class__.__name__, self.text)

    def is_text(self):
        return True


class LemmaNode(WordNetNode):
    qclass = cylleneus.engine.query.terms.Lemma
    tokenize = False
    removestops = False

    def __init__(self, text):
        self.fieldname = 'lemma'
        self.text = text
        self.boost = 1.0

    def __repr__(self):
        r = "<"
        if self.has_fieldname:
            r += "%r:" % self.fieldname
        r += f"<{self.text}>"
        if self.has_boost and self.boost != 1.0:
            r += " ^%s" % self.boost
        r += ">"
        return r

    def r(self):
        return repr(self)


class GlossNode(WordNetNode):
    qclass = cylleneus.engine.query.terms.Gloss
    tokenize = True
    removestops = False

    def __init__(self, text):
        self.fieldname = 'synset'
        self.text = text
        self.boost = 1.0

    def __repr__(self):
        r = "<"
        if self.has_fieldname:
            r += "%r:" % self.fieldname
        r += f"[{self.text}]"
        if self.has_boost and self.boost != 1.0:
            r += " ^%s" % self.boost
        r += ">"
        return r

    def r(self):
        return repr(self)


class SemfieldNode(WordNetNode):
    qclass = cylleneus.engine.query.terms.Semfield
    tokenize = True
    removestops = False

    def __init__(self, text):
        self.fieldname = 'semfield'
        self.text = text
        self.boost = 1.0

    def __repr__(self):
        r = "<"
        if self.has_fieldname:
            r += "%r:" % self.fieldname
        r += f"{{{self.text}}}"
        if self.has_boost and self.boost != 1.0:
            r += " ^%s" % self.boost
        r += ">"
        return r

    def r(self):
        return repr(self)


class AnnotationNode(WordNetNode):
    qclass = cylleneus.engine.query.terms.Annotation
    tokenize = True
    removestops = False

    def __init__(self, text):
        self.fieldname = 'annotation'
        self.text = text
        self.boost = 1.0

    def __repr__(self):
        r = "<"
        if self.has_fieldname:
            r += "%r:" % self.fieldname
        r += f"{self.text}"
        if self.has_boost and self.boost != 1.0:
            r += " ^%s" % self.boost
        r += ">"
        return r

    def r(self):
        return repr(self)


class AnnotationFilterNode(WordNetNode):
    qclass = cylleneus.engine.query.terms.Annotation
    tokenize = True
    removestops = False

    def __init__(self, text):
        self.fieldname = 'annotation'
        self.text = text
        self.boost = 1.0

    def __repr__(self):
        r = "<"
        if self.has_fieldname:
            r += "%r:" % self.fieldname
        r += f"{self.text}"
        if self.has_boost and self.boost != 1.0:
            r += " ^%s" % self.boost
        r += ">"
        return r

    def r(self):
        return repr(self)


class MorphosyntaxNode(TextNode):
    qclass = cylleneus.engine.query.terms.Morphosyntax
    tokenize = True
    removestops = False

    def __init__(self, text):
        self.fieldname = 'morphosyntax'
        self.text = text
        self.boost = 1.0

    def __repr__(self):
        r = "<"
        if self.has_fieldname:
            r += "%r:" % self.fieldname
        r += f"{self.text}"
        if self.has_boost and self.boost != 1.0:
            r += " ^%s" % self.boost
        r += ">"
        return r

    def r(self):
        return repr(self)


class MappingNode(TextNode):
    qclass = cylleneus.engine.query.terms.Mapping
    tokenize = True
    removestops = False

    def __init__(self, text):
        self.fieldname = 'mapping'
        self.text = text
        self.boost = 1.0

    def __repr__(self):
        r = "<"
        if self.has_fieldname:
            r += "%r:" % self.fieldname
        r += f"{self.text}"
        if self.has_boost and self.boost != 1.0:
            r += " ^%s" % self.boost
        r += ">"
        return r

    def r(self):
        return repr(self)


class Whitespace(MarkerNode):
    """Abstract syntax tree node for ignorable whitespace.
    """

    def r(self):
        return " "

    def is_ws(self):
        return True


class BinaryGroup(CylleneusGroupNode):
    """Intermediate base class for group nodes that have two subnodes and
    whose ``qclass`` initializer takes two arguments instead of a list.
    """

    merging = False
    has_boost = False

    def query(self, parser):
        assert len(self.nodes) == 2

        qa = self.nodes[0].query(parser)
        qb = self.nodes[1].query(parser)
        if qa is None and qb is None:
            q = cylleneus.engine.query.qcore.NullQuery
        elif qa is None:
            q = qb
        elif qb is None:
            q = qa
        else:
            q = self.qclass(self.nodes[0].query(parser),
                            self.nodes[1].query(parser))

        return attach(q, self)


class Wrapper(CylleneusGroupNode):
    """Intermediate base class for nodes that wrap a single sub-node.
    """

    merging = False

    def query(self, parser):
        q = self.nodes[0].query(parser)
        if q:
            return attach(self.qclass(q), self)


class ErrorNode(CylleneusSyntaxNode):
    def __init__(self, message, node=None):
        self.message = message
        self.node = node

    def r(self):
        return "ERR %r %r" % (self.node, self.message)

    @property
    def startchar(self):
        return self.node.startchar

    @property
    def endchar(self):
        return self.node.endchar

    def query(self, parser):
        if self.node:
            q = self.node.query(parser)
        else:
            q = cylleneus.engine.query.qcore.NullQuery

        return attach(whoosh.query.error_query(self.message, q), self)


class AndGroup(CylleneusGroupNode):
    qclass = cylleneus.engine.query.compound.And


class OrGroup(CylleneusGroupNode):
    qclass = cylleneus.engine.query.compound.Or

    @classmethod
    def factory(cls, scale=1.0):
        class ScaledOrGroup(OrGroup):
            def __init__(self, nodes=None, **kwargs):
                if "scale" in kwargs:
                    del kwargs["scale"]
                super(ScaledOrGroup, self).__init__(nodes=nodes, scale=scale,
                                                    **kwargs)
        return ScaledOrGroup


class DisMaxGroup(CylleneusGroupNode):
    qclass = cylleneus.engine.query.compound.DisjunctionMax


class OrderedGroup(CylleneusGroupNode):
    qclass = cylleneus.engine.query.positional.Ordered


class AndNotGroup(BinaryGroup):
    qclass = cylleneus.engine.query.compound.AndNot


class AndMaybeGroup(BinaryGroup):
    qclass = cylleneus.engine.query.compound.AndMaybe


class RequireGroup(BinaryGroup):
    qclass = cylleneus.engine.query.compound.Require


class NotGroup(Wrapper):
    qclass = cylleneus.engine.query.wrappers.Not


class RangeNode(CylleneusSyntaxNode):
    """Syntax node for range queries.
    """

    has_fieldname = True

    def __init__(self, start, end, startexcl, endexcl):
        self.start = start
        self.end = end
        self.startexcl = startexcl
        self.endexcl = endexcl
        self.boost = 1.0
        self.fieldname = None
        self.kwargs = {}

    def r(self):
        b1 = "{" if self.startexcl else "["
        b2 = "}" if self.endexcl else "]"
        return "%s%r %r%s" % (b1, self.start, self.end, b2)

    def query(self, parser):
        fieldname = self.fieldname or parser.fieldname
        start = self.start
        end = self.end

        if parser.schema and fieldname in parser.schema:
            field = parser.schema[fieldname]
            if field.self_parsing():
                try:
                    q = field.parse_range(fieldname, start, end,
                                          self.startexcl, self.endexcl,
                                          boost=self.boost)
                    if q is not None:
                        return attach(q, self)
                except whoosh.qparser.QueryParserError:
                    e = sys.exc_info()[1]
                    return attach(whoosh.query.error_query(e), self)

            if start:
                start = whoosh.qparser.get_single_text(field, start, tokenize=False,
                                        removestops=False)
            if end:
                end = whoosh.qparser.get_single_text(field, end, tokenize=False,
                                      removestops=False)

        q = cylleneus.engine.query.ranges.TermRange(fieldname, start, end, self.startexcl,
                                                    self.endexcl, boost=self.boost)
        return attach(q, self)


class CollocationGroup(CylleneusGroupNode):
    qclass = cylleneus.engine.query.positional.Collocation


class SequenceGroup(CylleneusGroupNode):
    merging = True
    qclass = cylleneus.engine.query.positional.Sequence

# CylleneusSyntaxNode = CylleneusSyntaxNode
# GroupNode = CylleneusGroupNode
