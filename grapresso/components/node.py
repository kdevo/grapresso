from typing import Iterable, Hashable

from .edge import Edge


class Node:
    def __init__(self, name, balance=0):
        """Constructs a node with a name."""
        self._edges = []
        self._name = name
        self._balance = balance

    @property
    def name(self) -> Hashable:
        return self._name

    @property
    def balance(self) -> float:
        return self._balance if self._balance else 0.0

    @property
    def neighbours(self) -> Iterable['Node']:
        return [edge.other_node_than(self) for edge in self._edges]

    def add_edge(self, edge):
        self._edges.append(edge)

    @property
    def edges(self) -> Iterable[Edge]:
        edges = []
        for edge in self._edges:
            if self == edge.from_node:
                edges.append(edge)
            else:
                edges.append(edge.inverse())
        return edges

    def edge(self, neighbour_node: 'Node') -> Edge:
        for edge in self.edges:
            if edge.to_node == neighbour_node:
                return edge
        raise KeyError("There is no neighbour '{}' accessible from node {}!".format(neighbour_node, self))

    def __str__(self):
        return "Node '{}'".format(self._name)

    def __repr__(self):
        return "Node '{}'".format(self._name)

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def updated_sorted_edges(self) -> Iterable[Edge]:
        self._edges.sort(key=lambda e: e.cost)
        return self.edges

    @property
    def is_source(self) -> bool:
        return self._balance > 0.0

    @property
    def is_sink(self) -> bool:
        return self._balance < 0.0


class IndexedNode(Node):
    """IndexedNode extends Node so that it is more efficient to find specific neighbours.
    This is accomplished by using an internal neighbour -> edge mapping.

    Attention: A symmetric edge needs to be created twice.
    """

    def __init__(self, name, balance=None):
        super().__init__(name, balance)
        self._indexed_edges = {}

    def add_edge(self, edge: Edge):
        super().add_edge(edge)
        self._indexed_edges[edge.other_node_than(self)] = edge

    def edge(self, neighbour_node: Node) -> Edge:
        try:
            return self._indexed_edges[neighbour_node]
        except KeyError:
            raise KeyError("There is no neighbour '{}' accessible from node '{}'!".format(neighbour_node, self))

    @property
    def neighbours(self) -> Iterable[Node]:
        return [edge.to_node for edge in self._edges]

    @property
    def edges(self) -> Iterable[Edge]:
        return self._edges
