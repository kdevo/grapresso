from abc import ABC, abstractmethod
from typing import Iterable, Hashable, Any

from grapresso.components.edge import Edge
from grapresso.components.node import Node


class DataBackend(ABC):
    @abstractmethod
    def __getitem__(self, node_name: Hashable) -> Node:
        """Get a node by node id.
        Implementations should try to guarantee O(1) access.

        Args:
            node_name: Node to get

        Returns:
            A node object matching to node_id

        """
        pass

    @abstractmethod
    def __contains__(self, node_name: Hashable) -> bool:
        """Check if a specific node_name is in the data structure.
        Implementations should try to guarantee O(1) access.

        Args:
            node_name: Node to check

        Returns:
            True if node_id exists else False
        """
        pass

    @abstractmethod
    def __iter__(self) -> Iterable[Node]:
        """Get an iterator that can be used to iterate through the data structure's node objects.

        Returns:
            Iterator that can be used in a loop
        """
        pass

    @abstractmethod
    def __len__(self):
        """Retrieve the amount of nodes stored in the data structure.

        Returns:
            Number of nodes in the data structure.
        """
        pass

    @abstractmethod
    def add_node(self, node_name: Hashable, **attributes):
        """Add a node_name.
        This variable can be anything that properly implements __hash__ and therewith __eq__).
        Use a str or an int if you want to keep things simple.

        Raises:
            NodeAlreadyExists: If the node_name already exists.

        Args:
            node_name: Node to add to the data structure.
        """
        pass

    @abstractmethod
    def add_edge(self, from_node_name: Hashable,
                 to_node_name: Hashable, symmetric: bool = False, **attributes):
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
        pass

    @abstractmethod
    def remove_edge(self, from_node_name: Hashable, to_node_name: Hashable):
        pass

    @abstractmethod
    def remove_node(self, node_name: Hashable):
        """Remove node with a specific node_name.

             Args:
                 node_name: Node to remove from the data structure.
        """
        pass

    @abstractmethod
    def node_names(self) -> Iterable[Hashable]:
        """Get all stored node names.

        Returns:
            An iterable of all node names in the data structure.
        """
        pass

    @abstractmethod
    def edges(self) -> Iterable[Edge]:
        """View with all edges from all nodes.
        In some implementations, this iterable can already be pre-saved so that some algorithms will run faster.

        Returns:
            Iterable for all edges of all nodes.
        """
        pass

    @property
    @abstractmethod
    def mst_alg_hint(self) -> str:
        """Backends can define their own recommendation for minimal spanning tree (MST) creation algorithms.
        Sometimes, backends "know" that a specific algorithm is faster because they define their inner graph structure
        by themselves and know themselves best.

        Returns:
            Either "kruskal" or "prim"
        """
        pass

    @property
    @abstractmethod
    def costminflow_alg_hint(self) -> str:
        """Backends can define their own recommendation for minimal cost, maximum flow algorithms.
        Sometimes, backends "know" that a specific algorithm is faster because they define their inner graph structure
        by themselves and know themselves best.

        Returns:
            Either "cycle-cancelling" or "successive-shortest-path"
        """
        pass

    @property
    @abstractmethod
    def data(self) -> Any:
        """Returns actual data held by the backend.
        This can be anything, since this API is data-agnostic and implementations should be free to use the format.

        Returns:
            Actual data representation (raw)

        """
        pass


class NodeAlreadyExistsError(ValueError):
    def __init__(self, node_name):
        super().__init__(f"Node with the name {node_name} already exists!")


class EdgeAlreadyExistsError(ValueError):
    def __init__(self, from_node_name, to_node_name):
        super().__init__(f"Edge ({from_node_name}, {to_node_name}) already exists!")
