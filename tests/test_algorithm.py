import math

from grapresso import DiGraph, BiGraph
from grapresso.backend.memory import InMemoryBackend
from grapresso.components.path import Flow


class TestAlgorithm:
    def test_breadth_search(self, create_backend):
        g = DiGraph(create_backend()) \
            .add_edge(1, 2) \
            .add_edge(1, 2) \
            .add_edge(2, 3) \
            .add_edge(2, 1)

        visited = [n.name for n in g.perform_dfs(1, None)]
        assert 1 in visited and 2 in visited and 3 in visited and 4 not in visited

    def test_depth_search(self, create_backend):
        g = DiGraph(create_backend()) \
            .add_edge(1, 2) \
            .add_edge(1, 2) \
            .add_edge(2, 3) \
            .add_edge(2, 1)

        visited = [n.name for n in g.perform_dfs(1, None)]
        assert 1 in visited and 2 in visited and 3 in visited and 4 not in visited

    def test_depth_vs_breath_search(self, create_backend):
        g = DiGraph(create_backend()) \
            .add_edge("a", "b") \
            .add_edge("a", "c") \
            .add_edge("c", "d") \
            .add_edge('d', 'e')

        l1 = []
        g.perform_dfs('a', lambda n: l1.append(n.name))
        assert ''.join(l1) == "acdeb"

        l2 = []
        g.perform_bfs('a', lambda n: l2.append(n.name))
        assert ''.join(l2) == "abcde"

        assert l1 != l2

    def test_full_enumeration(self, create_backend):
        g = BiGraph(create_backend()) \
            .add_edge("Aachen", "Amsterdam", cost=230) \
            .add_edge("Amsterdam", "Brussels", cost=200) \
            .add_edge("Brussels", "Aachen", cost=142)

        print(g.enumerate("Aachen").all_tours)

        # Now also add Luxembourg:
        for city, w in zip(("Aachen", "Brussels", "Amsterdam"), (200, 212, 420)):
            g.add_edge(city, "Luxembourg", cost=w)

        #            A m s t e r d a m ---------
        #      200 /                   \ 230    |
        # Brussels---------142---------Aachen   | 420
        #     142 \                   / 200     |
        #          L u x e m b o u r g ---------

        tours = g.enumerate("Aachen", True)
        print(tours.all_tours)
        # Number of tours must backend `(n-1)!` but we ignore the "direction" - that's why we multiply with 0.5.
        # For example: "a -> b -> c -> a" is the same as "a -> c -> b -> a" (i.e. "a <-> b <-> c <-> a")
        assert len(tours.all_tours) == math.factorial(len(g._nodes_data) - 1) * 0.5

    def test_shortest_tour(self, create_backend):
        g = BiGraph(create_backend()) \
            .add_edge("Aachen", "Amsterdam", cost=230) \
            .add_edge("Amsterdam", "Brussels", cost=200) \
            .add_edge("Brussels", "Aachen", cost=142)

        assert g.cheapest_tour("Aachen").cost == 572

        # Now also add Luxembourg:
        for city, c in zip(("Aachen", "Brussels", "Amsterdam"), (200, 212, 420)):
            g.add_edge(city, "Luxembourg", cost=c)

        tour = g.cheapest_tour("Aachen")
        assert tour.cost == 842
        print(tour)

    def test_residual(self, create_backend):
        graph = DiGraph(create_backend()) \
            .add_edge("Aachen", "Amsterdam", cost=230, capacity=100) \
            .add_edge("Amsterdam", "Brussels", cost=200, capacity=60) \
            .add_edge("Brussels", "Aachen", cost=142, capacity=50)

        res_graph, edges_info = graph.build_residual_graph(DiGraph(InMemoryBackend()),
                                                           Flow({graph.edge("Aachen", "Amsterdam"): 55}))
        assert res_graph.edge("Aachen", "Amsterdam").capacity == 45
        assert res_graph.edge("Amsterdam", "Aachen").capacity == 55

    def test_get_edge(self, create_backend):
        graph = BiGraph(create_backend()) \
            .add_edge("Aachen", "Amsterdam", cost=230, capacity=100) \
            .add_edge("Amsterdam", "Brussels", cost=200, capacity=60) \
            .add_edge("Brussels", "Aachen", cost=142, capacity=50)

        edge = graph[("Aachen", "Amsterdam")]
        assert edge.capacity == 100
