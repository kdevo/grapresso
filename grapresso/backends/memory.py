import itertools
from enum import Enum, unique
from typing import Iterable, Any, Hashable, Dict, Tuple

from .api import DataBackend, NodeAlreadyExistsError, EdgeAlreadyExistsError
from grapresso.components.node import Node
from ..components.edge import Edge


class InMemoryEdge(Edge):
    def __init__(self, u: 'Node', v: 'Node', **data: Dict[str, Any]):
        self._data = data
        self._u = u
        self._v = v

    @property
    def from_node(self) -> 'Node':
        return self._u

    @property
    def to_node(self) -> 'Node':
        return self._v

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
        return InMemoryEdge(self._v, self._u, **self._data)

    @property
    def data(self) -> Dict[str, Any]:
        return self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value


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
        # FIXME(kdevo): Due to heavy refactoring, dna is not integrated anymore
        self._id_to_node = {}

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
        self._id_to_node[node_name] = Node(node_name, **attributes)

    # def remove_node(self, node_id):
    #     self._id_to_node.pop(node_id)

    def node_names(self):
        return self._id_to_node.keys()

    def add_edge(self, u, v, symmetric: bool = False, **attributes):
        if v in self[u].edges:
            raise EdgeAlreadyExistsError(u, v)
        edge = InMemoryEdge(self[u], self[v], **attributes)
        self._id_to_node[u].connect(edge)
        if symmetric:
            self.add_edge(v, u, **attributes)

    def edges(self) -> Iterable[Edge]:
        return itertools.chain(*[n.edges for n in self])

    @property
    def mst_alg_hint(self) -> str:
        return 'prim'

    def remove_edge(self, u: Hashable, v: Hashable):
        del self[u].adj[v]
        # raise NotImplementedError(f"Remove is not yet implemented for {__name__}")

    def remove_node(self, node_name: Hashable):
        for v in self:
            if node_name in v.adj:
                self.remove_edge(node_name, v)
        del self._id_to_node[node_name]

    @property
    def costminflow_alg_hint(self) -> str:
        return 'successive-shortest-path'

    @property
    def data(self) -> Any:
        return self._id_to_node

    def __setstate__(self, state: Tuple[Dict, Dict]):
        self._id_to_node = {}
        node_data, flat_adj = state
        for u, data in node_data.items():
            self.add_node(u, **data)
        for u, adj in flat_adj.items():
            for v, data in adj:
                self.add_edge(u, v, **data)

    def __getstate__(self):
        flat_adj = {}
        node_data = {}
        for n in self:
            node_data[n.name] = n.data
            flat_adj[n.name] = [(e.v.name, e.data) for e in n.edges]
        return node_data, flat_adj
