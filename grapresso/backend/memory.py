import itertools
from enum import Enum, unique
from typing import Iterable, Any, Hashable, Dict

from .api import DataBackend, NodeAlreadyExistsError, EdgeAlreadyExistsError
from grapresso.components.node import Node, IndexedNode
from ..components.edge import Edge


class InMemoryEdge(Edge):
    def __init__(self, from_node: 'Node', to_node: 'Node', cost: float = None, capacity: float = None,
                 **kwargs: Dict[str, Any]):
        self._from_node = from_node
        self._to_node = to_node
        self._data = {}
        if cost:
            self._data['cost'] = cost
        if capacity:
            self._data['capacity'] = capacity
        for k, v in kwargs:
            self._data[k] = v

    @property
    def from_node(self) -> 'Node':
        return self._from_node

    @property
    def to_node(self) -> 'Node':
        return self._to_node

    @property
    def cost(self) -> float:
        return self._data.get('cost', 0.0)

    @cost.setter
    def cost(self, cost):
        self._data['cost'] = cost

    @property
    def capacity(self) -> float:
        return self._data.get('capacity', 0.0)

    @capacity.setter
    def capacity(self, cap):
        self._data['capacity'] = cap

    def inverse(self) -> 'Edge':
        return InMemoryEdge(self._to_node, self._from_node, **self._data)

    @property
    def data(self) -> Dict[str, Any]:
        return self._data


class InMemoryEdge2(Edge):
    def __init__(self, from_node: 'Node', to_node: 'Node',
                 cost: float = None, capacity: float = None, **kwargs: Dict[str, Any]):
        self._from_node = from_node
        self._to_node = to_node
        self._cost = cost
        self._capacity = capacity
        # self._data = {}
        # for k, v in kwargs:
        #     self._data[k] = v

    @property
    def from_node(self) -> 'Node':
        return self._from_node

    @property
    def to_node(self) -> 'Node':
        return self._to_node

    @property
    def cost(self) -> float:
        return self._cost if self._cost else 0.0

    @cost.setter
    def cost(self, cost):
        self._cost = cost

    @property
    def capacity(self) -> float:
        return self._capacity if self._capacity else 0.0

    @capacity.setter
    def capacity(self, cap):
        self._capacity = cap

    def inverse(self) -> 'Edge':
        return InMemoryEdge(self._to_node, self._from_node, self._cost, self._capacity)

    @property
    def data(self) -> Dict[str, Any]:
        return self._data


# TODO(kdevo): Fix
# InMemoryEdge = InMemoryEdge2


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
        edge = InMemoryEdge(self[from_node_name], self[to_node_name], **attributes)
        self._id_to_node[from_node_name].connect(edge)
        if symmetric:
            if self._dna == Trait.OPTIMIZE_PERFORMANCE:
                self.add_edge(to_node_name, from_node_name, **attributes)
            else:
                self._id_to_node[to_node_name].connect(edge)

    def edges(self) -> Iterable:
        return itertools.chain(*[n.edges for n in self])

    @property
    def mst_alg_hint(self) -> str:
        return 'prim'

    def remove_edge(self, from_node_name: Hashable, to_node_name: Hashable):
        raise NotImplementedError(f"Remove is not yet implemented for {__name__}")

    def remove_node(self, node_name: Hashable):
        raise NotImplementedError(f"Remove is not yet implemented for {__name__}")

    @property
    def costminflow_alg_hint(self) -> str:
        return 'successive-shortest-path'

    @property
    def data(self) -> Any:
        return self._id_to_node
