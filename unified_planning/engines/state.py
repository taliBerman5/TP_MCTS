import unified_planning as up
from typing import Tuple, List, Set

import numpy as np

class State(up.model.state.ROState):
    def __init__(self, predicates: Set["up.model.fnode.Fnode"] = None):
        self._predicates = predicates if predicates else set()


    def __eq__(self, other):
        if isinstance(other, State):
            return self.predicates == other.predicates
        return False

    def __hash__(self):
        res = hash("")
        for p in self._predicates:
            res += hash(p)
        return res

    @property
    def predicates(self):
        return self._predicates

    def set_predicates(self, new_predicates: Set):
        self._predicates = new_predicates

    def get_value(self):
        return 0

