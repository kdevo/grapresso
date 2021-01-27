import math
from collections import deque
from heapq import heappush, heappop
from typing import Optional, Set, Union, Callable, Iterable, Hashable, Tuple, Collection

from grapresso.components.edge import Edge
from grapresso.components.node import Node
from .api import BellmanFordResult, DistanceTable, DistanceEntry, MstResult
from ..backends.api import DataBackend
from ..backends.memory import InMemoryBackend
from ..components.path import CircularTour, TourTracker, Path, Cycle, Flow
from ..datastruct.disjointset import DefaultDisjointSet


class DiGraph:
    def __init__(self, data_backend: DataBackend = None):
        if data_backend is None:
            self._nodes_data = InMemoryBackend()
        else:
            self._nodes_data = data_backend

    @property
    def backend(self) -> DataBackend:
        """This property offers direct backend access. Use with care.
        In the long term, this property needs to be made redundant by offering direct Graph API methods as abstraction.

        Returns: Backend that has been used during initialisation.

        """
        return self._nodes_data

    def __getitem__(self, item: Union[Node, Hashable]) -> Union[Optional[Node], Optional[Edge]]:
        return self._nodes_data[item]

    # TODO(kdevo): Untested
    def __contains__(self, item):
        try:
            if isinstance(item, Edge):
                return self[item.v.name].edge(item.u.name) is not None
            elif isinstance(item, Node):
                return self[item.name] is not None
            else:
                return self[item] is not None
        except KeyError:
            return False

    def union(self, other: 'DiGraph'):
        for e in other.edges():
            if e in self:
                self[e.u.name, e.v.name].data = e.data
            else:
                self.add_edge(e.u.name, e.v.name, **e.data)
        return self

    # TODO(kdevo): Untested
    @classmethod
    def from_edges(cls, edges: Iterable[Edge], backend: DataBackend = None):
        net = cls(backend)
        for e in edges:
            if e.u.name not in net:
                net.add_node(e.u.name, **e.u.data)
            if e.v.name not in net:
                net.add_node(e.v.name, **e.u.data)
            net.add_edge(e.u.name, e.v.name, **e.data)
        return net

    # TODO(kdevo): Untested
    def from_tuples(self, *args: Union[Hashable, Tuple]):
        for it in args:
            if not isinstance(it, tuple):
                self.add_node(it)
            else:
                if 1 >= len(it) >= 4 or len(it) == 3 and not isinstance(it[2], dict):
                    raise ValueError("Only tuples from 1 to 3 values are allowed, "
                                     "where (u, v) means edge from u to v and with an optional data dict {} such as "
                                     "(u, v, {'k': 'val'}) and (u, {'k': 'val'}) means node u with a data dict.")
                elif len(it) == 2 and isinstance(it[1], dict):
                    self.add_node(it[0], **it[1])
                elif len(it) == 3 and isinstance(it[2], dict):
                    self.add_edge(it[0], it[1], **it[2])
                else:
                    self.add_edge(it[0], it[1])
        return self

    def nodes(self):
        return self.__iter__()

    def node_names(self):
        return self.backend.node_names()

    def copy_to(self, graph: 'DiGraph'):
        for n in self:
            graph.add_node(n.name)
        for e in self.edges():
            graph.add_edge(e.from_node.name, e.to_node.name, **e.data)
        return graph

    def edges(self, from_node=None, to_node=None) -> Collection[Edge]:
        return [e for e in self._nodes_data.edges()
                if (not from_node or e.from_node == from_node) and (not to_node or e.to_node == to_node)]

    def symmetric_edges(self, from_node=None, to_node=None):
        return [e for e in self.edges(from_node, to_node) if e.v.edge(e.u)]

    def node(self, start_node_name: Optional[Hashable]) -> Optional[Node]:
        """Convenience helper: Returns a (random) start_node if it is None.

        Args:
            start_node_name: Start node identifier/name

        Returns
            start_node if start_node is not None else a random node from the graph.
        """
        try:
            return next(iter(self._nodes_data)) if start_node_name is None else self._nodes_data[start_node_name]
        except KeyError:
            return None

    def __iter__(self):
        return iter(self._nodes_data)

    def free_node_name(self, wished_name: str = "Node") -> str:
        """Returns a free node name based on wished_name using a numeric suffix.

        Args:
            wished_name: The base name to try.

        Returns:
            wished_name [+ suffix_no]
        """

        def new_name(start_name, suffix_no):
            return start_name + str(suffix_no)

        if wished_name not in self._nodes_data:
            return wished_name
        else:
            count = 1
            wished_name = new_name(wished_name, count)
            while wished_name in self._nodes_data:
                count += 1
                wished_name = new_name(wished_name, count)
            return wished_name

    def add_edge(self, from_node_name, to_node_name, **attributes):
        if from_node_name not in self._nodes_data:
            self.add_node(from_node_name)
        if to_node_name not in self._nodes_data:
            self.add_node(to_node_name)
        self._nodes_data.add_edge(from_node_name, to_node_name, **attributes)
        return self

    def add_node(self, node_name, **attributes):
        self._nodes_data.add_node(node_name, **attributes)
        return self

    def remove_node(self, node_name):
        self._nodes_data.remove_node(node_name)

    def remove_edge(self, from_node, to_node):
        self._nodes_data.remove_edge(from_node, to_node)

    def edge(self, from_node_name, to_node_name) -> Optional[Edge]:
        try:
            node = self[from_node_name]
            if node:
                return node.edge(self._nodes_data[to_node_name])
        except KeyError:
            return None

    def perform_dfs(self, start_node_name=None, on_visited_cb: callable = None):
        start_node_name = self[start_node_name]
        seen = set()
        to_visit = [start_node_name]
        seen.add(start_node_name)

        while len(to_visit) > 0:
            current_node = to_visit.pop()
            for neighbour in current_node.neighbours:
                if neighbour not in seen:
                    to_visit.append(neighbour)
                    seen.add(neighbour)
            if on_visited_cb:
                on_visited_cb(current_node)
        return seen

    def perform_bfs(self, start_node_name=None, on_visited_cb: Callable[[Node], None] = None):
        start_node_name = self[start_node_name]
        seen = set()
        to_visit = deque(maxlen=len(self._nodes_data))
        to_visit.append(start_node_name)
        seen.add(start_node_name)

        while len(to_visit) > 0:
            current_node = to_visit.popleft()
            for neighbour in current_node.neighbours:
                if neighbour not in seen:
                    to_visit.append(neighbour)
                    seen.add(neighbour)
            if on_visited_cb:
                on_visited_cb(current_node)
        return seen

    def perform_kruskal(self, on_new_edge_cb: Callable[[Edge], None] = None) -> float:
        dj_set = DefaultDisjointSet(self._nodes_data)

        cost = 0
        sorted_edges = sorted(self._nodes_data.edges(), key=lambda e: e.cost)

        for edge in sorted_edges:
            if dj_set.find(edge.from_node) != dj_set.find(edge.to_node):
                dj_set.union(edge.from_node, edge.to_node)
                cost += edge.cost
                if on_new_edge_cb:
                    on_new_edge_cb(edge)

        return cost

    def build_mst(self, initialized_graph, preferred_algorithm=None) -> MstResult:
        costs = {'kruskal': self.perform_kruskal, 'prim': self.perform_prim}[
            preferred_algorithm if preferred_algorithm else self._nodes_data.mst_alg_hint](
            on_new_edge_cb=lambda e: initialized_graph.add_edge(e.from_node.name, e.to_node.name, cost=e.cost)
        )
        return MstResult(costs, initialized_graph)

    def perform_prim(self, start_node_name=None, on_new_edge_cb: callable = None) -> int:
        to_visit = set(self._nodes_data)
        current_node = self[start_node_name]

        sorted_connections = []
        mst_costs = 0

        while len(to_visit) - 1 > 0:
            to_visit.remove(current_node)

            for edge in current_node.edges:
                if edge.to_node in to_visit:
                    heappush(sorted_connections, (edge.cost, edge))

            next_candidate = heappop(sorted_connections)

            # check if the next_candidate is already visited and if sorted_neighbours is not empty
            while next_candidate[1].to_node not in to_visit and len(sorted_connections) > 0:
                next_candidate = heappop(sorted_connections)

            if on_new_edge_cb:
                on_new_edge_cb(next_candidate[1])
            current_node = next_candidate[1].to_node  # to_node
            mst_costs += next_candidate[0]  # cost

        return mst_costs

    def perform_bellman_ford(self, start_node_name=None) -> BellmanFordResult:
        """"

        """
        start_node = self[start_node_name]
        dist_table = {start_node: DistanceEntry(None, 0.0)}

        def dist(node):
            return dist_table[node].dist if node in dist_table else math.inf

        for _ in range(len(self._nodes_data) - 1):
            updated_dist = False
            for edge in self._nodes_data.edges():
                if dist(edge.from_node) + edge.cost < dist(edge.to_node):
                    dist_table[edge.to_node] = DistanceEntry(edge.from_node, dist(edge.from_node) + edge.cost)
                    updated_dist = True
            if not updated_dist:
                break

        for edge in self._nodes_data.edges():
            if dist(edge.from_node) + edge.cost < dist(edge.to_node):
                # Construct negative cycle:
                node = edge.from_node
                visited_nodes = set()
                potential_edges = deque()
                # Go back via parent nodes and optimistically collect the edges:
                while node not in visited_nodes:
                    parent_node = dist_table[node].parent
                    potential_edges.append(self.edge(parent_node.name, node.name))
                    visited_nodes.add(node)
                    node = parent_node

                # Only go edges that actually belong to the found cycle:
                cycle = Cycle(node)
                edge = potential_edges.pop()
                while edge.to_node != node:
                    cycle.go(edge)
                    edge = potential_edges.pop()
                return BellmanFordResult(dist_table, cycle.finish())

        return BellmanFordResult(dist_table, None)

    def perform_dijkstra(self, start_node_name=None) -> DistanceTable:
        start_node = self[start_node_name]
        dist_table = {start_node: DistanceEntry(None, 0.0)}
        visited = set()
        sorted_nodes = [(0.0, start_node)]

        def dist(node):
            return dist_table[node].dist if node in dist_table else math.inf

        while len(sorted_nodes) > 0:
            cheapest_node = heappop(sorted_nodes)
            for edge in cheapest_node[1].edges:
                new_distance = dist(edge.from_node) + edge.cost
                if new_distance < dist(edge.to_node):
                    dist_table[edge.to_node] = DistanceEntry(edge.from_node, new_distance)
                    if cheapest_node not in visited:
                        heappush(sorted_nodes, (new_distance, edge.to_node))
            visited.add(cheapest_node)

        return dist_table

    def cheapest_path(self, start_node_name, end_node_name):
        bmr = self.perform_bellman_ford(start_node_name)
        return Path.from_tree(lambda v: bmr.dist_table[v].parent, self[start_node_name], self[end_node_name])

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Directed graph with {} nodes".format(len(self._nodes_data))

    def __len__(self):
        return len(self._nodes_data)

    def __sizeof__(self):
        return self._nodes_data.__sizeof__()

    def build_residual_graph(self, initialized_residual_graph: 'DiGraph', flow: Flow):
        edge_info = {}

        for edge in self._nodes_data.edges():
            fw_capacity = edge.capacity - flow[edge]
            bw_capacity = flow[edge]
            if fw_capacity > 0:
                initialized_residual_graph.add_edge(edge.from_node.name, edge.to_node.name,
                                                    capacity=fw_capacity, cost=edge.cost)
                fw_edge = initialized_residual_graph.edge(edge.from_node.name, edge.to_node.name)
                edge_info[fw_edge] = (edge, True)

            if bw_capacity > 0:
                initialized_residual_graph.add_edge(edge.to_node.name, edge.from_node.name,
                                                    capacity=bw_capacity, cost=-edge.cost)
                bw_edge = initialized_residual_graph.edge(edge.to_node.name, edge.from_node.name)
                edge_info[bw_edge] = (edge, False)

        return initialized_residual_graph, edge_info

    def shortest_path(self, source_node_name, target_node_name) -> Optional[Path]:
        # TODO(kdevo): Refactor real bfs instead for the first part of this algorithm:
        source_node, target_node = self[source_node_name], self[target_node_name]
        node_to_parent = {source_node: None}

        to_visit = deque(maxlen=len(self._nodes_data))
        to_visit.append(source_node)
        found_path = False

        while not found_path and len(to_visit) > 0:
            current_node = to_visit.popleft()
            for edge in current_node.edges:
                neighbour = edge.to_node
                if neighbour not in node_to_parent:
                    to_visit.append(neighbour)
                    node_to_parent[neighbour] = current_node
                    if neighbour == target_node:
                        found_path = True

        if found_path:
            return Path.from_tree(lambda v: node_to_parent[v], source_node, target_node)
        else:
            return None

    def perform_edmonds_karp(self, source_node_name, target_node_name) -> Flow:
        # Initialize flow. Set ∀ e ∈ E: f(e) = 0:
        flow = Flow()
        path_in_resgraph_exists = True

        while path_in_resgraph_exists:
            # Calculate G' and u':
            res_graph, res_edge_to_orig = self.build_residual_graph(DiGraph(InMemoryBackend()), flow)
            # Find (s,t)-path p ∈ G' and also therewith determine γ = min(u'(e)) with e ∈ p:
            augmenting_path = res_graph.shortest_path(source_node_name, target_node_name)
            if augmenting_path is None:
                path_in_resgraph_exists = False
            else:
                # Augment f around γ using (s,t)-path p
                flow.augment_along_path(augmenting_path, res_edge_to_orig)
        return flow

    def perform_cycle_cancelling(self) -> Flow:
        # Create a virtual SUPER-SOURCE s and SUPER-TARGET t
        s_name, t_name = self.free_node_name("SUPER-SOURCE"), self.free_node_name("SUPER-TARGET")
        s_out_flow, t_in_flow = 0, 0
        for n in list(self._nodes_data.node_names()):
            node = self._nodes_data[n]
            if node.is_source:
                s_out_flow += node.balance
                self.add_edge(s_name, node.name, capacity=node.balance)
            elif node.is_sink:
                t_in_flow += abs(node.balance)
                self.add_edge(node.name, t_name, capacity=abs(node.balance))

        # Check if flow is conserved:
        if t_in_flow == s_out_flow:
            # Get an initial flow:
            flow = self.perform_edmonds_karp(s_name, t_name)
            # Check if the found flow really is a valid balanced flow (b-flow).
            # Since s_out_flow == t_in_flow we only need to check the super source's outgoing edges:
            if sum(flow[e] for e in self[s_name].edges) != s_out_flow:
                raise ValueError("No balanced flow possible: Unsatisfied balance(s)! "
                                 "The edges' capacities are too small.")
        else:
            raise ValueError("Flow conversation is not possible (out {} != in {})!".format(s_out_flow, t_in_flow))

        # Now that we have a valid b-flow, we can start the iterations until no cost-negative cycle is found anymore:
        while True:
            # Calculate G', u', c':
            res_graph, res_edge_to_orig = self.build_residual_graph(DiGraph(InMemoryBackend()), flow)

            # We can also find negative cycles when the graph's connected component is bigger than 1.
            # That is why we need to test if there is a negative cycle from all start nodes:
            start_nodes = set(self._nodes_data)
            result = None
            while len(start_nodes) > 0:
                start_node = start_nodes.pop()
                result = res_graph.perform_bellman_ford(start_node.name)
                if result.is_cycle_detected:
                    break
                start_nodes -= result.visited

            if result.is_cycle_detected:
                # Augment f around γ using negative cycle
                flow.modify_along_path(result.cycle, res_edge_to_orig, result.cycle.min_capacity)
            else:
                # If we cannot find a negative cycle anymore, we found an optimal solution:
                return flow

    def perform_successive_shortest_path(self) -> Flow:
        pseudo_balances = {}

        def pseudo_balances_satisfied():
            for v in self._nodes_data:
                if v.balance != pseudo_balances[v]:
                    return False
            return True

        flow = Flow()

        # Use to capacity u(e) for edges with negative costs:
        for edge in self._nodes_data.edges():
            if edge.cost < 0:
                flow[edge] = edge.capacity
            else:
                flow[edge] = 0

        # Calculate initial pseudo balances: b'(v) = outflow - inflow
        for node in self._nodes_data:
            pseudo_balances[node] = sum(flow[e] for e in node.edges) \
                                    - sum(flow[e] for e in self._nodes_data.edges() if e.to_node == node)

        while not pseudo_balances_satisfied():
            # Calc residual graph G', we need it when checking if the target is accessible from the source:
            res_graph, res_edge_to_orig = self.build_residual_graph(DiGraph(InMemoryBackend()), flow)

            try:
                # Find a pseudo source s, where we need to saturate the outflow in G':
                pseudo_s = next(filter(
                    lambda v: v.balance - pseudo_balances[v] > 0,
                    self._nodes_data
                ))
                # Find pseudo target t, where we need to saturate the inflow in G' AND t must be reachable from s:
                pseudo_t = next(filter(
                    lambda v: v.balance - pseudo_balances[v] < 0 and res_graph.shortest_path(pseudo_s.name, v.name),
                    self._nodes_data
                ))
            except StopIteration:
                raise ValueError("No balanced flow possible: Could not find a valid pair source and target!")

            # Cost-cheapest path is constructed using Bellman-Ford algorithm and iterating through the resulting tree:
            path = res_graph.cheapest_path(pseudo_s.name, pseudo_t.name)

            t_balance_diff = pseudo_balances[pseudo_t] - pseudo_t.balance
            s_balance_diff = pseudo_s.balance - pseudo_balances[pseudo_s]
            gamma = min(path.min_capacity, t_balance_diff, s_balance_diff)

            flow.modify_along_path(path, res_edge_to_orig, gamma)
            pseudo_balances[pseudo_s] += gamma
            pseudo_balances[pseudo_t] -= gamma
        flow.max_flow = sum([n.balance for n in self._nodes_data if n.balance > 0])
        return flow


class UnDiGraph(DiGraph):
    def add_edge(self, a, b, **kwargs):
        if a not in self._nodes_data:
            self.add_node(a)
        if b not in self._nodes_data:
            self.add_node(b)
        self._nodes_data.add_edge(a, b, True, **kwargs)
        return self

    def perform_nearest_neighbour_tour(self, start_node_name=None):
        """Criteria: Fully connected | Undirected

        Args:
            start_node_name: Name of the start node.

        Returns:
            CircularTour
        """

        to_visit = set(self._nodes_data)
        node = self[start_node_name]
        with CircularTour(node) as nn_tour:
            while len(to_visit) - 1 > 0:
                to_visit.remove(node)
                edge = next(e for e in node.sorted_edges() if e.to_node in to_visit)
                nn_tour.go(edge)
                node = edge.to_node
        return nn_tour

    def double_tree_tour(self, start_node_name=None):
        mst_result = self.build_mst(UnDiGraph(InMemoryBackend()))
        visited_node_names = []
        mst_result.tree.perform_dfs(start_node_name, on_visited_cb=lambda n: visited_node_names.append(n.name))
        with CircularTour(self[start_node_name]) as dt_tour:
            for i in range(0, len(visited_node_names) - 1):
                for edge in self._nodes_data[visited_node_names[i]].edges:
                    if edge.to_node == self._nodes_data[visited_node_names[i + 1]]:
                        dt_tour.go(edge)
        return dt_tour

    def enumerate(self, start_node_name=None, track_all=False) -> TourTracker:
        def go_recursive_step(current_edge: Edge, current_tour: CircularTour, all_tours):
            current_tour.go(current_edge)
            current_node = current_edge.to_node
            non_visited = [e for e in current_node.edges if e.to_node not in current_tour.visited]
            # Node with "degree" >= 1 means we have a branch node:
            if len(non_visited) >= 1:
                # Create a new branch for each unvisited neighbour:
                for edge in non_visited:
                    go_recursive_step(edge, current_tour.branch(), all_tours)
            # Node with degree 0 means we have a leaf - the end of the tour:
            else:
                all_tours.add(current_tour.finish())

        start_node = self[start_node_name]
        tours = TourTracker(only_store_cheapest=not track_all)
        # Initial step is done here so that there is more clarity in the recursive function.
        # (n-1) nodes and edges to start with (neighbours) because we have a fully connected graph:
        for start_edge in start_node.edges:
            go_recursive_step(start_edge, CircularTour(start_node), tours)
        return tours

    def enumerate_bnb(self, start_node_name=None) -> CircularTour:
        def go_recursive_step(current_edge: Edge, current_tour: CircularTour, all_tours):
            current_tour.go(current_edge)
            if current_tour.cost < all_tours.cheapest_tour.cost:
                current_node = current_edge.to_node
                non_visited = [e for e in current_node.edges if e.to_node not in current_tour.visited]
                # Node with degree >= 1 means we have a branch node:
                if len(non_visited) >= 1:
                    # Create a new branch for each unvisited neighbour:
                    for edge in non_visited:
                        go_recursive_step(edge, current_tour.branch(), all_tours)
                # Node with "degree" >= 1 means we have a leaf - the end of the tour:
                else:
                    all_tours.add(current_tour.finish())

        nn_tour = self.perform_nearest_neighbour_tour(start_node_name)
        start_node = self[start_node_name]

        tours = TourTracker()
        tours.add(nn_tour)

        # Initial step is done here so that there is more clarity in the recursive function.
        # (n-1) nodes and edges to start with (neighbours) because we have a fully connected graph:
        for start_edge in start_node.edges:
            go_recursive_step(start_edge, CircularTour(start_node), tours)
        return tours.cheapest_tour

    def cheapest_tour(self, start_node_name=None) -> CircularTour:
        return self.enumerate_bnb(start_node_name)

    def count_connected_components(self):
        remaining_nodes = set(self._nodes_data)
        start_node = next(iter(remaining_nodes))
        total_connected_count = 0
        while start_node:
            remaining_nodes -= self.perform_dfs(start_node.name)
            total_connected_count += 1
            start_node = next(iter(remaining_nodes), None)

        return total_connected_count

    def is_connected(self):
        return self.count_connected_components() == 1

    def max_matchings(self, node_names_a: Set, node_names_b: Set):
        # Create a directed graph
        directed_graph = DiGraph(InMemoryBackend())
        for edge in self._nodes_data.edges():
            if edge.from_node.name in node_names_a and edge.to_node.name in node_names_b:
                directed_graph.add_edge(edge.from_node.name, edge.to_node.name, capacity=1)

        # Create super source and super target because we use Edmonds Karp later to get a max. flow:
        s_name, t_name = directed_graph.free_node_name("SUPER-SOURCE"), directed_graph.free_node_name("SUPER-TARGET")
        for node_name in list(directed_graph._nodes_data.node_names()):
            if node_name in node_names_a:
                directed_graph.add_edge(s_name, node_name, capacity=1)
            elif node_name in node_names_b:
                directed_graph.add_edge(node_name, t_name, capacity=1)

        flow = directed_graph.perform_edmonds_karp(s_name, t_name)
        matched_edges = []
        for e in flow.edges():
            if e.from_node.name in node_names_a and e.to_node.name in node_names_b:
                matched_edges.append(self.edge(e.from_node.name, e.to_node.name))
        return matched_edges

    def __repr__(self):
        return "Undirected graph with {} nodes".format(len(self._nodes_data))
