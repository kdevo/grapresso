from grapresso.backend.memory import InMemoryBackend
from grapresso.components.graph import DiGraph
from grapresso.components.path import CircularTour


class TestTour:
    def test_tour(self):
        g = DiGraph(InMemoryBackend()) \
            .add_edge(1, 2) \
            .add_edge(1, 2) \
            .add_edge(2, 3) \
            .add_edge(2, 1)

        start_node = g.node_by_name(1)
        tour = CircularTour(start_node)
        tour.go(next(iter(start_node.edges)))
        assert tour.start_node == start_node
        assert start_node in tour.visited
        assert len(list(tour)) == 1

        tour.finish()
        assert len(list(tour)) == 2
        assert tour.edges[-1].to_node == tour.start_node
        print(tour)
