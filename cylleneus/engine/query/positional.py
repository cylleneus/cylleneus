import engine.query.compound


class Sequence(engine.query.compound.CylleneusCompoundQuery):
    """Matches documents containing a list of sub-queries in adjacent
    positions.
    This object has no sanity check to prevent you from using queries in
    different fields.
    """

    JOINT = " THEN "
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


class Collocation(engine.query.compound.CylleneusCompoundQuery):
    """Matches documents containing a list of sub-queries in identical
    positions.
    This object has no sanity check to prevent you from using queries in
    different fields.
    """

    JOINT = " WITH "
    intersect_merge = True

    def __init__(self, subqueries, slop=0, ordered=True, boost=1.0, meta=False):
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
        from engine.query.qcore import Every
        from engine.query.ranges import TermRange, NumericRange

        # Normalize subqueries and merge nested instances of this class
        subqueries = []
        for s in self.subqueries:
            s = s.normalize()
            if isinstance(s, self.__class__):
                subqueries += [ss.with_boost(ss.boost * s.boost) for ss in s]
            else:
                subqueries.append(s)

        # If every subquery is Null, this query is Null
        if all(q is engine.query.qcore.NullQuery for q in subqueries):
            return engine.query.qcore.NullQuery

        # If there's an unfielded Every inside, then this query is Every
        if any((isinstance(q, Every) and q.fieldname is None)
               for q in subqueries):
            return Every()

        # Merge ranges and Everys
        everyfields = set()
        i = 0
        while i < len(subqueries):
            q = subqueries[i]
            f = q.field()
            if f in everyfields:
                subqueries.pop(i)
                continue

            if isinstance(q, (TermRange, NumericRange)):
                j = i + 1
                while j < len(subqueries):
                    if q.overlaps(subqueries[j]):
                        qq = subqueries.pop(j)
                        q = q.merge(qq, intersect=self.intersect_merge)
                    else:
                        j += 1
                q = subqueries[i] = q.normalize()

            if isinstance(q, Every):
                everyfields.add(q.fieldname)
            i += 1

        # Eliminate duplicate queries
        subqs = []
        seenqs = set()
        for s in subqueries:
            if not isinstance(s, Every) and s.field() in everyfields:
                continue
            if s in seenqs:
                continue
            seenqs.add(s)
            subqs.append(s)

        # Remove NullQuerys
        subqs = [q for q in subqs if q is not engine.query.qcore.NullQuery]

        if not subqs:
            return engine.query.qcore.NullQuery

        if len(subqs) == 1:
            sub = subqs[0]
            sub_boost = getattr(sub, "boost", 1.0)
            if not (self.boost == 1.0 and sub_boost == 1.0):
                sub = sub.with_boost(sub_boost * self.boost)
            return sub

        return self.__class__(subqs, boost=self.boost)

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
        m = engine.query.spans.SpanWith2(subs).matcher(searcher, context)
        return m


class Ordered(Sequence):
    """Matches documents containing a list of sub-queries in the given order.
    """

    JOINT = " BEFORE "

    def _matcher(self, subs, searcher, context):
        from engine.query.spans import SpanBefore

        return self._tree_matcher(subs, SpanBefore._Matcher, searcher,
                                  context, None)
