import itertools
from enum import Enum, unique
from typing import Iterable

from .api import DataBackend, NodeAlreadyExistsError, EdgeAlreadyExistsError
from grapresso.components.edge import Edge
from grapresso.components.node import Node, IndexedNode


@unique
class Trait(Enum):
    """Traits to choose from when using the InMemoryBackend.

    OPTIMIZE_MEMORY:
        Optimize memory consumption in return for less algorithmic performance.
        Initial graph building is faster though.

    OPTIMIZE_PERFORMANCE:
        Optimize algorithmic performance in return for more memory consumption.
        Initial graph building is slower due to more involved data structures.

    Recommendation: Use OPTIMIZE_MEMORY for undirected graphs and OPTIMIZE_PERFORMANCE for directed graphs.
    This is because undirected graphs would otherwise store the edge (a, b) twice as (a, b) and (b, a).

    See Also:
        `DataBackend` API `add_edge` function.
    """
    OPTIMIZE_MEMORY = 1
    OPTIMIZE_PERFORMANCE = 2


class InMemoryBackend(DataBackend):
    """This backend holds all nodes in-memory using a key-value storage (dict).

    It allows you to specify a trait.

    See Also:
        `Trait` class for the choices.
    """

    def __init__(self, dna: Trait = Trait.OPTIMIZE_PERFORMANCE):
        self._id_to_node = {}
        self._dna = dna

    def __iter__(self):
        return self._id_to_node.values().__iter__()

    def __contains__(self, node_name):
        return self._id_to_node.__contains__(node_name)

    def __getitem__(self, node_name):
        return self._id_to_node[node_name]

    def __len__(self):
        return self._id_to_node.__len__()

    def add_node(self, node_name, **attributes):
        if node_name in self._id_to_node:
            raise NodeAlreadyExistsError(node_name)
        if self._dna is Trait.OPTIMIZE_PERFORMANCE:
            self._id_to_node[node_name] = IndexedNode(node_name, **attributes)
        else:
            self._id_to_node[node_name] = Node(node_name, **attributes)

    # def remove_node(self, node_id):
    #     self._id_to_node.pop(node_id)

    def node_names(self):
        return self._id_to_node.keys()

    def add_edge(self, from_node_name, to_node_name, symmetric: bool = False, **attributes):
        if to_node_name in self._id_to_node[from_node_name].edges:
            raise EdgeAlreadyExistsError(from_node_name, to_node_name)
        edge = Edge(self[from_node_name], self[to_node_name], **attributes)
        self._id_to_node[from_node_name].add_edge(edge)
        if symmetric:
            if self._dna == Trait.OPTIMIZE_PERFORMANCE:
                self.add_edge(to_node_name, from_node_name, **attributes)
            else:
                self._id_to_node[to_node_name].add_edge(edge)

    def edges(self) -> Iterable:
        return itertools.chain(*[n.edges for n in self])

    @property
    def mst_alg_hint(self) -> str:
        return 'prim'
