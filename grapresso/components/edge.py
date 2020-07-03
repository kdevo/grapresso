from abc import ABC, abstractmethod
from typing import Any, Hashable, Dict


class Connection(ABC):
    @abstractmethod
    def __init__(self, to_node: 'Node', **kwargs: Dict[str, Any]):
        pass

    @property
    @abstractmethod
    def to_node(self) -> 'Node':
        pass

    @property
    def v(self) -> 'Node':
        return self.to_node

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

    def __lt__(self, other):
        return self.cost < other.cost

    def __gt__(self, other):
        return self.cost > other.cost

    @property
    @abstractmethod
    def data(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def key(self) -> Hashable:
        return self.to_node

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        # TODO(kdevo): Evaluate if this exact type check is faster than using isinstance (which is often recommended)
        return self.__class__ is other.__class__ and other.key == self.key

    def __str__(self):
        return f"➔ {self.to_node}"

    def __repr__(self):
        return f"➔ {repr(self.to_node)} (${self.cost}{f', ^{self.capacity}' if self.capacity != 0 else ''})"


class Edge(Connection):
    @abstractmethod
    def __init__(self, from_node: 'Node', to_node: 'Node', cost: float = None, capacity: float = None,
                 **kwargs: Dict[str, Any]):
        pass

    @property
    def u(self) -> 'Node':
        return self.from_node

    @property
    @abstractmethod
    def from_node(self) -> 'Node':
        pass

    def opposite(self, of_node: 'Node') -> 'Node':
        return self.from_node if of_node == self.to_node else self.to_node

    def __str__(self):
        return f"{self.from_node} {super().__str__()}"

    def __repr__(self):
        return f"{repr(self.from_node)} {super().__repr__()}"

    @abstractmethod
    def inverse(self) -> 'Edge':
        pass

    @property
    def key(self) -> Hashable:
        return self.from_node, self.to_node
