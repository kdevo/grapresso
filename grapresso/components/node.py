from typing import Sized

from .edge import Edge
from ..datastruct.typing import Collection


class Node:
    def __init__(self, name, balance=None):
        """Constructs a node with a name."""
        self._edges = []
        self._name = name
        self._balance = balance

    @property
    def name(self):
        return self._name

    @property
    def balance(self):
        return self._balance if self._balance else 0.0

    @property
    def neighbours(self) -> Collection:
        return [edge.other_node_than(self) for edge in self._edges]

    def add_edge(self, edge):
        self._edges.append(edge)

    @property
    def edges(self) -> Collection:
        edges = []
        for edge in self._edges:
            if self == edge.from_node:
                edges.append(edge)
            else:
                edges.append(edge.inverse())
        return edges

    def edge(self, neighbour_node) -> Edge:
        for edge in self.edges:
            if edge.to_node == neighbour_node:
                return edge
        raise KeyError("There is no neighbour '{}' accessible from node {}!".format(neighbour_node, self))

    def __str__(self):
        return "Node '{}' ({count} edges)".format(self._name, count=len(self.edges))

    def __repr__(self):
        return "{}".format(self._name)

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def updated_sorted_edges(self):
        self._edges.sort(key=lambda e: e.cost)
        return self.edges

    @property
    def is_source(self):
        return self._balance > 0.0

    @property
    def is_sink(self):
        return self._balance < 0.0


class IndexedNode(Node):
    """IndexedNode extends Node so that it is more efficient to find specific neighbours.
    This is accomplished by using an internal neighbour -> edge mapping.

    Attention: A symmetric edge needs to be created twice.
    """
    def __init__(self, name, balance=None):
        super().__init__(name, balance)
        self._indexed_edges = {}

    def add_edge(self, edge):
        super().add_edge(edge)
        self._indexed_edges[edge.other_node_than(self)] = edge

    def edge(self, neighbour_node):
        try:
            return self._indexed_edges[neighbour_node]
        except KeyError:
            raise KeyError("There is no neighbour '{}' accessible from node '{}'!".format(neighbour_node, self))

    @property
    def neighbours(self) -> Collection:
        return [edge.to_node for edge in self._edges]

    @property
    def edges(self) -> Collection:
        return self._edges


class FileNode(Node):
    def __init__(self, name, backend, balance=None):
        """
        Construct a node with a name holding a backend.

        Args:
            name: Name of the node (this is a unique ID)
            backend: The backend parameter is needed to reconstruct actual edge objects
        """
        super().__init__(name, balance)
        self._backend = backend

    @property
    def neighbours(self) -> Sized:
        return [self._backend[e.to_node] for e in self._edges]

    @property
    def edges(self) -> Collection:
        return [Edge(self._backend[self._name], self._backend[e.to_node], e.cost, e.capacity) for e in self._edges]

    def __setstate__(self, state):
        # Prevent _backend from being deserialized
        self._name, self._balance, self._edges = state

    def __getstate__(self):
        # Prevent _backend from being serialized
        return self._name, self._balance, self._edges

    def edge(self, neighbour_node) -> Edge:
        for edge in self.edges:
            if edge.to_node == neighbour_node:
                return edge
        raise KeyError("There is no neighbour '{}' accessible from node {}!".format(neighbour_node, self))