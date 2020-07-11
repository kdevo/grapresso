from typing import Iterable, Hashable, Any, Dict

import networkx as nx

from grapresso.backends.api import DataBackend
from grapresso.components.edge import Edge
from grapresso.components.node import Node


class NxEdge(Edge):
    """NxEdge is a "virtual" edge:
    Basically it does not store any attributes except from_node and to_node references.
    All properties are computed by using the NetworkX graph structure itself.

    """

    def __init__(self, from_node: 'Node', to_node: 'Node', nx_edge: Dict[Hashable, Any]):
        self._from_node = from_node
        self._to_node = to_node
        self._edge_data = nx_edge

    @property
    def cost(self) -> float:
        return self._edge_data.get('cost', 0.0)

    @cost.setter
    def cost(self, cost):
        self._edge_data['cost'] = cost

    @property
    def capacity(self) -> float:
        return self._edge_data.get('capacity', 0.0)

    @capacity.setter
    def capacity(self, cap):
        self._edge_data['capacity'] = cap

    @property
    def to_node(self) -> 'Node':
        return self._to_node

    @property
    def from_node(self) -> 'Node':
        return self._from_node

    def __getattr__(self, item):
        val = self._edge_data[item]
        self.__setattr__(item, val)
        return val

    @property
    def data(self) -> Dict[Hashable, Any]:
        return self._edge_data

    def inverse(self) -> 'Edge':
        return NxEdge(self.to_node, self.from_node, self._edge_data)


class NxNode(Node):
    def __init__(self, nx_graph: nx.DiGraph, name, balance=None, **kwargs):
        self._nxg = nx_graph
        self._name = name

    @property
    def balance(self) -> float:
        return self._nxg.nodes[self]['balance']

    @balance.setter
    def balance(self, balance):
        self._nxg.nodes[self]['balance'] = balance

    def _build(self, name):
        return NxNode(self._nxg, name, **self._nxg.nodes[name])

    @property
    def neighbours(self) -> Iterable[Node]:
        neighbours = [self._build(n) for n in self._nxg.neighbors(self)]
        return neighbours

    def edge(self, neighbour_node: 'Node') -> Edge:
        data = self._nxg[self][neighbour_node]
        return NxEdge(self, self._build(neighbour_node), data)

    @property
    def edges(self) -> Iterable[Edge]:
        edges = [NxEdge(self, self._build(e[1]), e[2]) for e in self._nxg.edges(self.name, data=True)]
        return edges

    # TODO(kdevo): Untested
    def connect(self, edge: Edge):
        self._nxg.add_edge(self, edge.to_node, **edge.data)

    def sorted_edges(self) -> Iterable[Edge]:
        return sorted(self.edges, key=lambda e: e.cost)


class NetworkXBackend(DataBackend):
    """ Allows you to use NetworkX as a backend!
    Grapresso functions as a middleman with a unified API here.
    This enables you to use all algorithms NetworkX provides by accessing the underlying nx_graph.

    Warnings:
        Still in Beta:
        - Could be better performance-wise:
            - Reconstructing the "node-local" edges takes time
            - Node data is partly stored duplicated
        - NetworkX uses different concepts, so we need to use some (more or less) hacky tricks here
    """

    @property
    def data(self) -> Any:
        return self.nx_graph

    def __init__(self, directed=True):
        self._nx = nx.DiGraph() if directed else nx.Graph()
        # TODO(kdevo): Try to use a node factory method here to increase performance

    @property
    def nx_graph(self) -> nx.DiGraph:
        return self._nx

    def __getitem__(self, node_name: Hashable) -> Node:
        return NxNode(self._nx, node_name, self._nx.nodes[node_name])

    def __contains__(self, node_name: Hashable) -> bool:
        return node_name in self._nx.nodes.keys()

    def __iter__(self) -> Iterable[Node]:
        return [self[n] for n in self._nx.nodes.keys()].__iter__()

    def __len__(self):
        return len(self._nx)

    def add_node(self, node_name: Hashable, **attributes) -> None:
        self._nx.add_node(node_name, **attributes)

    def add_edge(self, from_node_name: Hashable, to_node_name: Hashable, symmetric: bool = False, **attributes) -> None:
        self._nx.add_edge(from_node_name, to_node_name, **attributes)
        if symmetric:
            self._nx.add_edge(to_node_name, from_node_name, **attributes)

    def remove_edge(self, from_node_name: Hashable, to_node_name: Hashable):
        self._nx.remove_edge(from_node_name, to_node_name)

    def remove_node(self, node_name: Hashable):
        self._nx.remove_node(node_name)

    def node_names(self) -> Iterable[Hashable]:
        return {k for k in self._nx.nodes.keys()}

    def edges(self) -> Iterable[Edge]:
        edges = self._nx.edges.data(default={})
        return [NxEdge(self[e[0]], self[e[1]], e[2]) for e in edges]

    @property
    def mst_alg_hint(self) -> str:
        return 'prim'

    @property
    def costminflow_alg_hint(self) -> str:
        return 'successive-shortest-path'

    def quick_draw(self, pos=None, ax=None, edge_label_selector='cost', mark_edges=None, **kwargs):
        import matplotlib.pyplot as plt
        graph = self._nx
        defaults = {
            'mark_edges': mark_edges,
            'node_color': '#0097a7',
            'node_size': 700,
            'edge_label_pos': 0.42,
            'edge_labels': {(e.from_node, e.to_node): e[edge_label_selector]
                            for e in self.edges()} if edge_label_selector else None,
        }

        kw_dict = {**defaults, **kwargs}
        pos = pos if pos else nx.spring_layout(self._nx)
        if kw_dict['edge_labels']:
            nx.draw_networkx_edge_labels(
                graph, pos,
                edge_labels=kw_dict['edge_labels'],
                label_pos=kw_dict['edge_label_pos'],
                font_weight=kw_dict.get('edge_font_weight', kw_dict.get('font_weight'))
            )
        if kw_dict['mark_edges']:
            nx.draw_networkx_edges(graph, pos,
                                   edgelist=[(e.from_node, e.to_node) for e in kw_dict['mark_edges']],
                                   edge_color='#0097a7',
                                   width=kw_dict.get('edge_width', 1) * 4)
        nx.draw_networkx(graph, pos, ax, **kw_dict)

        plt.axis('off')
        plt.show()
