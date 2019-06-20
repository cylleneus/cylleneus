import engine.query.compound


class Sequence(engine.query.compound.CylleneusCompoundQuery):
    """Matches documents containing a list of sub-queries in adjacent
    positions.
    This object has no sanity check to prevent you from using queries in
    different fields.
    """

    JOINT = " NEAR "
    intersect_merge = True

    def __init__(self, subqueries, slop=1, ordered=True, boost=1.0, meta=False):
        """
        :param subqueries: a list of :class:`whoosh.query.Query` objects to
            match in sequence.
        :param slop: the maximum difference in position allowed between the
            subqueries.
        :param ordered: if True, the position differences between subqueries
            must be positive (that is, each subquery in the list must appear
            after the previous subquery in the document).
        :param boost: a boost factor to add to the score of documents matching
            this query.
        """

        engine.query.compound.CylleneusCompoundQuery.__init__(self, subqueries, boost=1.0)
        self.slop = slop
        self.ordered = ordered
        self.meta = meta
        self.boost = boost if boost > 1 else len(subqueries)
        for i, subq in enumerate(subqueries):
            subq.boost = self.boost
            subq.pos = i
        if any([subq.meta for subq in subqueries]):
            self.meta = True
            self.slop = 2 if slop < 2 else slop

    def __eq__(self, other):
        return (other and type(self) is type(other)
                and self.subqueries == other.subqueries
                and self.boost == other.boost)

    def __repr__(self):
        return "%s(%r, slop=%d, boost=%f)" % (self.__class__.__name__,
                                              self.subqueries, self.slop,
                                              self.boost)

    def __hash__(self):
        h = hash(self.slop) ^ hash(self.boost)
        for q in self.subqueries:
            h ^= hash(q)
        return h

    def normalize(self):
        # Because the subqueries are in sequence, we can't do the fancy merging
        # that CompoundQuery does
        return self.__class__([q.normalize() for q in self.subqueries],
                              self.slop, self.ordered, self.boost)

    def _and_query(self):
        return engine.query.compound.And(self.subqueries)

    def estimate_size(self, ixreader):
        return self._and_query().estimate_size(ixreader)

    def estimate_min_size(self, ixreader):
        return self._and_query().estimate_min_size(ixreader)

    def _matcher(self, subs, searcher, context):
        import engine.query.spans

        # Tell the sub-queries this matcher will need the current match to get
        # spans
        context = context.set(needs_current=True)
        m = self._tree_matcher(subs, engine.query.spans.SpanNear.SpanNearMatcher, searcher,
                               context, None, slop=self.slop,
                               ordered=self.ordered)
        return m


class Ordered(Sequence):
    """Matches documents containing a list of sub-queries in the given order.
    """

    JOINT = " BEFORE "

    def _matcher(self, subs, searcher, context):
        from engine.query.spans import SpanBefore

        return self._tree_matcher(subs, SpanBefore._Matcher, searcher,
                                  context, None)
