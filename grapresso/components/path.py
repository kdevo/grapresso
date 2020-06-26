from collections import defaultdict, deque
from collections.abc import Iterable

import math

from grapresso.components.node import Node
from grapresso.components.edge import Edge
from ..datastruct.typing import Collection


class Path:
    def __init__(self, source_node, target_node):
        self._source_node = source_node
        self._target_node = target_node

        self._cost = 0
        self._min_capacity = math.inf
        self._all_edges = []

        self._visited = {source_node}
        self._incremental_hash = hash(source_node)

    def go(self, edge: Edge):
        # Check if the previous edge's neighbour is the current edge's from_node [i.e. chain (v, w), (w, u)]:
        if len(self._all_edges) > 1 and self._all_edges[-1].to_node != edge.from_node:
            raise ValueError("Broken chain: Cannot go an edge that is not accessible from '{}'!".format(edge.from_node))
        self._all_edges.append(edge)
        self._cost += edge.cost
        self._min_capacity = min(self._min_capacity, edge.capacity)
        self._visited.add(edge.from_node)
        # TODO(kdevo): Revise if incrementing hash like is sufficient:
        self._incremental_hash += hash((edge.from_node, edge.to_node)) + hash((edge.to_node, edge.from_node))
        return self

    def run(self, edges: Collection):
        for e in edges:
            self.go(e)
        return self

    def finish(self):
        last_node = self._all_edges[-1].to_node
        if last_node != self._target_node:
            self.go(last_node.edge(self._target_node))
        return self

    @property
    def cost(self):
        return self._cost

    @property
    def min_capacity(self):
        return self._min_capacity

    @property
    def visited(self):
        return self._visited

    @property
    def start_node(self):
        return self._source_node

    @property
    def end_node(self):
        return self._target_node

    @property
    def edges(self):
        return self._all_edges

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

    def __hash__(self):
        return hash((self._cost, self._incremental_hash))

    def __eq__(self, other):
        return isinstance(self, type(other)) and self._visited == other.visited \
               and self._incremental_hash == other._incremental_hash

    def branch(self):
        branched_tour = Path(self._source_node, self._target_node)
        branched_tour._incremental_hash = self._incremental_hash
        branched_tour._cost = self._cost
        branched_tour._visited = self._visited.copy()
        branched_tour._all_edges = self._all_edges.copy()
        return branched_tour

    def __copy__(self):
        return self.branch()

    def __iter__(self):
        return self._all_edges.__iter__()

    def __repr__(self):
        s = "Total cost: {} | Min. capacity: {} :: {}".format(self._cost, self._min_capacity, self._source_node.name)
        for e in self._all_edges:
            s += ' ---[^{}|${}]---> {}'.format(e.capacity, e.cost, e.to_node.name)
        return s

    @staticmethod
    def from_tree(parent_key: callable, source: Node, target: Node):
        node = target
        path_edges = deque()
        while node != source:
            parent = parent_key(node)
            path_edges.appendleft(parent.edge(node))
            node = parent
        return Path(source, target).run(path_edges)


class CircularTour(Path):
    def __init__(self, start_node):
        super().__init__(start_node, start_node)


class Cycle(CircularTour):
    def __init__(self, start_node):
        super().__init__(start_node)
    #
    # def go(self, edge: Edge):
    #     if self.start_node is None:
    #         self._start_node = edge.from_node
    #         self._end_node = edge.from_node
    #     super(CircularTour, self).go(edge)


class TourTracker:
    def __init__(self, only_store_cheapest=True):
        self._cheapest_tour = None
        self._only_store_cheapest = only_store_cheapest
        self._all = set()

    def add(self, tour: Path):
        if not self._cheapest_tour or tour.cost < self._cheapest_tour.cost:
            self._cheapest_tour = tour
        if not self._only_store_cheapest:
            self._all.add(tour)

    @property
    def all_tours(self) -> Iterable:
        return {self._cheapest_tour} if self._only_store_cheapest else self._all

    @property
    def cheapest_tour(self) -> CircularTour:
        return self._cheapest_tour


class Flow:
    def __init__(self, initialize_dict: {} = None):
        self._edge_to_flow = defaultdict(float)
        self._cost = 0
        self._max_flow = None
        if initialize_dict:
            for (e, f) in initialize_dict.items():
                self.set(e, f)

    def set(self, edge, flow):
        if 0 <= flow <= edge.capacity:
            flow_diff = flow - self._edge_to_flow[edge]
            self._cost += flow_diff * edge.cost
            self._edge_to_flow[edge] = flow
        else:
            raise ValueError("Flow must be between 0 and capacity {}!".format(edge.capacity))

    def increase(self, edge, flow):
        self.set(edge, self._edge_to_flow[edge] + flow)

    def decrease(self, edge, flow):
        self.set(edge, self._edge_to_flow[edge] - flow)

    @property
    def cost(self):
        return self._cost

    @property
    def max_flow(self):
        return self._max_flow

    @max_flow.setter
    def max_flow(self, value):
        self._max_flow = value

    def __getitem__(self, item):
        return self._edge_to_flow[item]

    def __setitem__(self, key, value):
        self.set(key, value)

    def edges(self):
        return [e for e in self._edge_to_flow if self._edge_to_flow[e] > 0]

    def augment_along_path(self, full_st_path: Path, res_edge_info: {}):
        if self._max_flow is None:
            self._max_flow = full_st_path.min_capacity
        else:
            self._max_flow += full_st_path.min_capacity
        self.modify_along_path(full_st_path, res_edge_info, full_st_path.min_capacity)

    def modify_along_path(self, path_part: Path, res_edge_info: {}, gamma):
        for res_edge in path_part:
            orig_edge = res_edge_info[res_edge][0]
            is_forward_edge = res_edge_info[res_edge][1]
            # If e ∈ G' is a FORWARD edge (→):
            if is_forward_edge:
                # Increase f(e) with e ∈ G around γ:
                self.increase(orig_edge, gamma)
            # If e ∈ G' is a BACKWARD edge (←):
            else:
                # Decrease f(e) with e ∈ G around γ:
                self.decrease(orig_edge, gamma)
