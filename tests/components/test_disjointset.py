from grapresso.datastruct.disjointset import DefaultDisjointSet


class TestDisjointSet:
    def test_find_and_union(self):
        djs = DefaultDisjointSet([1, 2, 3, 4, 5, 6])  # {1: {1}, 2: {2}, 3: {3}, ..}
        assert djs.find(1) != djs.find(2)
        djs.union(2, 1)  # {1: {1, 2}, 2: ref[1], ..} => {1: {1, 2}, 2: {1, 2}, ..}
        assert djs.find(1) == djs.find(2)
        djs.union(3, 1)  # {1: ref[3], 2: ref[1], 3: {1, 2, 3}}
        assert djs.find(3) == djs.find(1) and djs[1] == djs[3]  # Index op is syntactic sugar for find
        assert djs[2] == djs[3]
        assert djs[3] != djs[4]
        djs.union(4, 5)
        djs.union(5, 6)
        djs.union(4, 6)
        djs.union(6, 3)
        assert djs[6] == djs[1]
