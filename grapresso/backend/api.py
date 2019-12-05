from typing import Iterable

from ..components.node import Node


class DataBackend:
    def __getitem__(self, node_name) -> Node:
        """Get a node by node id.
        Implementations should try to guarantee O(1) access.

        Args:
            node_name: Node to get

        Returns:
            A node object matching to node_id

        """
        raise NotImplementedError()

    def __contains__(self, node_name):
        """Check if a specific node_name is in the data structure.
        Implementations should try to guarantee O(1) access.

        Args:
            node_name: Node to check

        Returns:
            True if node_id exists else False
        """
        raise NotImplementedError()

    def __iter__(self):
        """Get an iterator that can be used to iterate through the data structure's node objects.

        Returns:
            Iterator that can be used in a loop
        """
        raise NotImplementedError()

    def __len__(self):
        """Retrieve the amount of nodes stored in the data structure.

        Returns:
            Number of nodes in the data structure.
        """
        raise NotImplementedError()

    def add_node(self, node_name, **attributes):
        """Add a node_name.
        This variable can be anything that properly implements __hash__ and therewith __eq__).
        Use a str or an int if you want to keep things simple.

        Raises:
            NodeAlreadyExists: If the node_name already exists.

        Args:
            node_name: Node to add to the data structure.
        """
        raise NotImplementedError()

    def add_edge(self, from_node_name, to_node_name, symmetric: bool = False, **attributes):
        """Add an edge (from_node_name, to_node_name) = (x, y) with attributes to the graph.
        Per default, the edge is asymmetric/unidirectional (symmetric = False).
        For symmetric/bidirectional edges (x, y) = (y, x) implementations can consider to
            only store the edge once and then swap them when needed for memory efficiency.

        Raises:
            EdgeAlreadyExistsException: If the edge (from_node_name, to_node_name) already exists.

        Args:
            from_node_name: The tail node name is the "start".
            to_node_name: The head node name is the "end".
            symmetric: Specify if the edge is symmetric/undirected or asymmetric/directed.
            **attributes: Attributes can e.g. contain the cost (special key: "cost") or other data.
        """
        raise NotImplementedError()

    def remove_edge(self, from_node_name, to_node_name):
        raise NotImplementedError()

    def remove_node(self, node_name):
        """Remove node with a specific node_name.

             Args:
                 node_name: Node to remove from the data structure.
        """
        raise NotImplementedError()

    def node_names(self) -> Iterable:
        """Get all stored node names.

        Returns:
            An iterable of all node names in the data structure.
        """
        raise NotImplementedError()

    def edges(self) -> Iterable:
        """Get all edges from all nodes.
        In some implementations, this iterable can already be pre-saved so that some algorithms will run faster.

        Returns:
            Iterable for all edges of all nodes.
        """
        raise NotImplementedError()

    @property
    def mst_alg_hint(self) -> str:
        """Backends can define their own recommendation for minimal spanning tree (MST) creation algorithms.
        Sometimes, backends "know" that a specific algorithm is faster because they define their inner graph structure
        by themselves and know themselves best.

        Returns:
            Either "kruskal" or "prim"
        """
        raise NotImplementedError()

    @property
    def costminflow_alg_hint(self) -> str:
        """Backends can define their own recommendation for minimal cost, maximum flow algorithms.
        Sometimes, backends "know" that a specific algorithm is faster because they define their inner graph structure
        by themselves and know themselves best.

        Returns:
            Either "cycle-cancelling" or "successive-shortest-path"
        """
        raise NotImplementedError()


class NodeAlreadyExistsError(ValueError):
    def __init__(self, node_name):
        super().__init__("Node with the ID %s already exists!".format(node_name))


class EdgeAlreadyExistsError(ValueError):
    def __init__(self, from_node_name, to_node_name):
        super().__init__("Edge (%s, %s) already exists!".format(from_node_name, to_node_name))
