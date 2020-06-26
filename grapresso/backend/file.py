import itertools
import os
import pickle
from abc import ABC
from typing import Iterable, Sized

from grapresso.components.edge import Edge
from grapresso.components.node import Node
from .api import DataBackend, NodeAlreadyExistsError, EdgeAlreadyExistsError


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
    def edges(self) -> Iterable[Edge]:
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


class DirectoryBasedFileBackend(DataBackend, ABC):
    def __init__(self, base_dir):
        self._base_dir = os.path.abspath(base_dir)
        if not os.path.exists(self._base_dir):
            os.makedirs(base_dir)

    def __len__(self):
        return len(os.listdir(self._base_dir))


class PickleFileBackend(DirectoryBasedFileBackend):
    """FIXME(kdevo): This backend is highly inefficient and more a proof of work than production-ready."""

    def __getitem__(self, node_name) -> Node:
        with open(self._node_path(node_name), 'rb') as file:
            node = pickle.load(file)
            node._backend = self
            return node

    def __contains__(self, node_name):
        return os.path.exists(self._node_path(node_name))

    def __iter__(self):
        for file_name in os.listdir(self._base_dir):
            with open(os.path.join(self._base_dir, file_name), 'rb') as file:
                node = pickle.load(file)
                node._backend = self  # Inject self because backend is not unpickled
                yield node

    def add_node(self, node_name, **kwargs):
        if node_name in self:
            raise NodeAlreadyExistsError(node_name)
        with open(self._node_path(node_name), 'wb+') as file:
            pickle.dump(FileNode(node_name, self, **kwargs), file, pickle.HIGHEST_PROTOCOL)

    def _node_path(self, node_id):
        return os.path.join(self._base_dir, str(hash(node_id)) + '.node')

    def node_names(self):
        return {node.name for node in iter(self)}

    def add_edge(self, from_node_name, to_node_name, symmetric: bool = False, **attributes):
        node = self[from_node_name]
        if to_node_name in node.edges:
            raise EdgeAlreadyExistsError(from_node_name, to_node_name)
        # ATTENTION: Note that the Edge is built "shallowly" using only the node names!
        node.add_edge(Edge(from_node_name, to_node_name, **attributes))
        with open(self._node_path(from_node_name), 'wb+') as file:
            pickle.dump(node, file, pickle.HIGHEST_PROTOCOL)
        if symmetric:
            self.add_edge(to_node_name, from_node_name, False, **attributes)

    def edges(self) -> Iterable:
        return itertools.chain(*[n.edges for n in self])

    @property
    def mst_alg_hint(self) -> str:
        return 'prim'
