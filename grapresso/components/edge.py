from typing import Any, Hashable


class OutgoingConnection:
    def __init__(self, to_node, cost=None, capacity=None, **kwargs):
        self._to_node = to_node
        self._cost = cost
        self._capacity = capacity

    @property
    def to_node(self):
        return self._to_node

    @property
    def cost(self):
        return self._cost if self._cost else 0.0

    @property
    def capacity(self) -> float:
        return self._capacity if self._capacity else 0.0

    @capacity.setter
    def capacity(self, cap):
        self._capacity = cap

    def __str__(self):
        if self._capacity:
            return f"--[^{self.capacity}|${self.cost}]--> {self._to_node.name}"
        else:
            return f"--[${self.cost}]--> {self._to_node.name}"

    def __repr__(self):
        return self.__str__()


class Edge(OutgoingConnection):
    def __init__(self, from_node: 'Node', to_node: 'Node', cost: float = None, capacity: float = None,
                 data: Any = None):
        super().__init__(to_node, cost, capacity)
        self._from_node = from_node
        self._data = data

    @property
    def from_node(self):
        return self._from_node

    @property
    def data(self) -> Any:
        return self._data

    def inverse(self) -> 'Edge':
        return Edge(self._to_node, self._from_node, self._cost, self._capacity)

    def __str__(self):
        return "{} {}".format(self._from_node.name, super().__str__())

    def other_node_than(self, node) -> 'Node':
        return self._from_node if node == self._to_node else self._to_node

    def __lt__(self, other):
        return self.cost < other.cost

    # TODO(kdevo): Revise if the following is really necessary:
    def __key(self) -> Hashable:
        return self._from_node, self._to_node

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, Edge) and other.__key() == self.__key()
