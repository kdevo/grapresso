from typing import Iterable, Hashable, Dict, Any, Union

import grapresso.components.edge as edge


class Node:
    def __init__(self, name, **kwargs):
        """Constructs a node with a name."""
        self._adj = {}
        self._name = name
        self._data = kwargs

    @property
    def name(self) -> Hashable:
        return self._name

    @property
    def balance(self) -> float:
        return self._data.get('balance', 0.0)

    @balance.setter
    def balance(self, value):
        self._data['balance'] = value

    def connect(self, edge):
        # TODO(kdevo): Refactor this to 'Connection' class
        self._adj[edge.opposite(self)] = edge
        # if edge.from_node != self and edge.to_node != self:
        #     raise ValueError()

    def edge(self, neighbour_node: Union['Node', Hashable]) -> 'edge.Edge':
        return self._adj.get(neighbour_node)

    def __str__(self):
        return f"Node '{self._name}' with {len(list(self.edges))} edges"

    def __repr__(self):
        return f"{repr(self._name)}"

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        return self._name == other

    def __lt__(self, other):
        return self.balance < other.balance

    # FIXME(kdevo): When later specifying the Node as ABC, this should be removed and handled externally,
    #  though it boosts performance 'on-demand' (that is when an algorithm needs it), but algorithms should be clearly
    #  divided from data access which is the purpose of this class.
    def sorted_edges(self) -> Iterable['edge.Edge']:
        return sorted(self.edges, key=lambda e: e.cost)

    @property
    def neighbours(self) -> Iterable['Node']:
        return self._adj.keys()

    @property
    def edges(self) -> Iterable['edge.Edge']:
        return self._adj.values()

    @property
    def is_source(self) -> bool:
        return self.balance > 0.0

    @property
    def is_sink(self) -> bool:
        return self.balance < 0.0

    def __getitem__(self, item):
        e = self.edge(item)
        if e is None:
            raise KeyError(f"There is no neighbour {item} accessible from node {self}")
        return e

    @property
    def data(self) -> Dict[str, Any]:
        return self._data

    def __len__(self):
        return len(self._adj.keys())

    # TODO(kdevo): Check why this causes stackoverflow while debugging:
    # def __getattr__(self, item):
    #     return self.data[item]
