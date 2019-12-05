from typing import NamedTuple, Dict, Optional

from .path import Cycle
from .node import Node

DistanceEntry = NamedTuple('DistanceEntry', [('parent', Optional[Node]), ('dist', float)])
DistanceTable = Dict[Node, DistanceEntry]


class BellmanFordResult:
    def __init__(self, dist_table: DistanceTable, cycle: Optional[Cycle]):
        self.dist_table = dist_table
        self.cycle = cycle

    @property
    def is_cycle_detected(self) -> bool:
        return self.cycle is not None

    @property
    def visited(self) -> set:
        return {v for v in self.dist_table}


class Graph:
    pass


MstResult = NamedTuple('MstResult', [('costs', float), ('mst', Graph)])
