from abc import ABC, abstractmethod
from typing import Any, Hashable, Dict


class Connection(ABC):
    @abstractmethod
    def __init__(self, to_node: 'Node',
                 cost: float = None, capacity: float = None, **kwargs: Dict[str, Any]):
        pass

    @property
    @abstractmethod
    def to_node(self) -> 'Node':
        pass

    @property
    @abstractmethod
    def cost(self) -> float:
        pass

    @cost.setter
    @abstractmethod
    def cost(self, cost):
        pass

    @property
    @abstractmethod
    def capacity(self) -> float:
        pass

    @capacity.setter
    @abstractmethod
    def capacity(self, cap):
        pass

    @abstractmethod
    def __getattr__(self, item):
        pass

    def __lt__(self, other):
        return self.cost < other.cost

    def __gt__(self, other):
        return self.cost > other.cost

    def __key(self) -> Hashable:
        return self.to_node

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, Connection) and other.__key() == self.__key()

    def __str__(self):
        return f" ➔ {self.to_node.name}"

    def __repr__(self):
        return self.__str__()


class Edge(Connection):
    @abstractmethod
    def __init__(self, from_node: 'Node', to_node: 'Node', cost: float = None, capacity: float = None,
                 **kwargs: Dict[str, Any]):
        super().__init__(to_node, cost, capacity, **kwargs)

    @property
    @abstractmethod
    def to_node(self) -> 'Node':
        pass

    def other_node_than(self, node) -> 'Node':
        return self.from_node if node == self.to_node else self.to_node

    def __key(self) -> Hashable:
        return self.from_node, self.to_node

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, Edge) and other.__key() == self.__key()

    def __str__(self):
        return f"{self.from_node} ➔ {self.__str__()}"

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def inverse(self) -> 'Edge':
        pass


class DefaultEdge(Edge):
    def __init__(self, from_node: 'Node', to_node: 'Node', cost: float = None, capacity: float = None,
                 **kwargs: Dict[str, Any]):
        super().__init__(from_node, to_node, cost, capacity, **kwargs)
        self._to_node = to_node
        self._from_node = from_node
        self._cost = cost
        self._capacity = capacity
        self._additional_data = kwargs

    @property
    def from_node(self) -> 'Node':
        return self._from_node

    def __getattr__(self, item):
        self.__setattr__(item, self._additional_data[item])

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
    def capacity(self, cap): self._capacity = cap

    def inverse(self) -> 'Edge':
        return DefaultEdge(self.to_node, self.from_node, self.cost, self.capacity)
