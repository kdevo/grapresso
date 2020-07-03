import pytest

from grapresso.components.node import Node


class TestBackend:
    """ Test the backends that implement the API.

    TODO(kdveo): Provide (more) meaningful tests.
    """

    def test_construction(self, create_backend):
        backend = create_backend()
        backend.add_node(1)
        backend.add_node(2)
        assert 1 in backend.node_names() and 2 in backend.node_names()

        backend.add_edge(1, 2, symmetric=True, cost=12)
        assert backend[1].edge(backend[2]).cost == 12
        assert backend[2].edge(backend[1]).cost == 12
        assert backend[1] in backend[2].neighbours
        assert 2 in [e.to_node.name for e in backend[1].edges]
        assert sum(1 for _ in backend.edges()) == 2

        backend.add_node('3')
        backend.add_node(4)
        backend.add_edge('3', 4, cost=1, capacity=10)
        edge = backend['3'].edge(backend[4])
        assert edge.cost == 1 and edge.capacity == 10
        with pytest.raises(KeyError):
            _ = backend[4].edge(backend['3'])

        assert {1, 2, '3', 4} == {n.name for n in backend}

    def test_modification(self, create_backend):
        nodes = create_backend()

        nodes.add_node('Berlin')
        nodes.add_node('Aachen')
        nodes.add_edge('Berlin', 'Aachen', symmetric=True, capacity=10)
        edge = nodes['Berlin'].edge('Aachen')
        assert edge.capacity == 10

        edge.capacity = 20
        assert edge.capacity == 20

