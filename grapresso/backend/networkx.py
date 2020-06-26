from typing import Iterable, Hashable

import networkx as nx

from grapresso.backend.api import DataBackend
from grapresso.components.edge import Edge
from grapresso.components.node import Node


class NetworkXNode(Node):
    def __init__(self, nx_graph: nx.DiGraph, name, balance=None):
        super().__init__(name, balance)
        self._nxg = nx_graph

    @property
    def neighbours(self) -> Iterable[Node]:
        neighbours = [self._nxg.nodes[n]['node'] for n in self._nxg.neighbors(self.name)]
        return neighbours

    def edge(self, neighbour_node: 'Node') -> Edge:
        data = self._nxg.adj[self.name][neighbour_node.name]
        return Edge(self, self._nxg.nodes[neighbour_node.name]['node'], **data)

    @property
    def edges(self) -> Iterable[Edge]:
        edges = [Edge(self, self._nxg.nodes[e[1]]['node'], **self._nxg.get_edge_data(e[0], e[1], default={}))
                 for e in self._nxg.edges(self.name)]
        return edges

    def add_edge(self, edge: Edge):
        self._nxg.add_edge(edge.from_node.name, edge.to_node.name,
                           cost=edge.cost, capacity=edge.capacity, data=edge.data)


# TODO(kdevo): This is still a huge WIP
class NetworkXBackend(DataBackend):
    def __init__(self):
        self.g = nx.DiGraph()

    def __getitem__(self, node_name: Hashable) -> NetworkXNode:
        return self.g.nodes[node_name]['node']

    def __contains__(self, node_name: Hashable) -> bool:
        return node_name in self.g.nodes.keys()

    def __iter__(self) -> Iterable[Node]:
        return [self[n] for n in self.g.nodes.keys()].__iter__()

    def __len__(self):
        return len(self.g)

    def add_node(self, node_name: Hashable, **attributes) -> None:
        node = NetworkXNode(self.g, node_name, **attributes)
        self.g.add_node(node_name, node=node)

    def add_edge(self, from_node_name: Hashable, to_node_name: Hashable, symmetric: bool = False, **attributes) -> None:
        from_node: NetworkXNode = self[from_node_name]
        to_node: NetworkXNode = self[to_node_name]
        edge = Edge(from_node, to_node, **attributes)
        from_node.add_edge(edge)
        if symmetric:
            to_node.add_edge(edge.inverse())

    def remove_edge(self, from_node_name: Hashable, to_node_name: Hashable):
        self.g.remove_edge(from_node_name, to_node_name)

    def remove_node(self, node_name: Hashable):
        self.g.remove_node(node_name)

    def node_names(self) -> Iterable[Hashable]:
        return {k for k in self.g.nodes.keys()}

    def edges(self) -> Iterable[Edge]:
        edges = self.g.edges.data(default={})
        return [Edge(self[e[0]], self[e[1]], **e[2]) for e in edges]

    @property
    def mst_alg_hint(self) -> str:
        return 'prim'

    @property
    def costminflow_alg_hint(self) -> str:
        return 'successive-shortest-path'
