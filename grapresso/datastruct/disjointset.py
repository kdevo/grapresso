from typing import Set


class DisjointSet:
    def union(self, e1, e2):
        raise NotImplementedError()

    def find(self, e1):
        raise NotImplementedError()

    def __getitem__(self, item):
        raise NotImplementedError()


class PrimitiveDisjointSet(DisjointSet):
    """Primitive Disjoint-set implementation that is more efficient than list-based Disjoint-sets,
    but worse than highly optimized implementations with path compression or similar.
    """

    def __init__(self, iterable):
        self._sets = {e: {e} for e in iterable}  # => make_sets => {e1: {e1}, e2: {e2}, ..}

    def union(self, e1, e2):
        # Swap e1 and e2 if e2 is longer to optimize iterations
        if len(self._sets[e1]) < len(self._sets[e2]):
            e1, e2 = e2, e1
        self._sets[e1] |= self._sets[e2]  # Unite set[e1] and set[e2]
        for e in self._sets[e2]:
            self._sets[e] = self._sets[e1]  # Set a reference to the set of e1

    def find(self, e) -> Set:
        return self._sets[e]

    def __getitem__(self, item):
        return self.find(item)


class DefaultDisjointSet(DisjointSet):
    """Disjoint set using path splitting and union by size. Pretty fast.
    Reference: https://en.wikipedia.org/wiki/Disjoint-set_data_structure
    """

    def __init__(self, iterable):
        self._data = {e: idx for idx, e in enumerate(iterable)}
        self._parents = list(range(len(self._data)))
        self._sizes = [1] * len(self._data)

    def find(self, x):
        idx = self._parents[self._data[x]]
        while self._parents[idx] != idx:
            idx, self._parents[idx] = self._parents[idx], self._parents[self._parents[idx]]
        return idx

    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)

        if x_root != y_root:
            if self._sizes[x_root] < self._sizes[y_root]:
                x_root, y_root = y_root, x_root
            self._parents[y_root] = x_root
            self._sizes[x_root] += self._sizes[y_root]

    def __getitem__(self, item):
        return self.find(item)
