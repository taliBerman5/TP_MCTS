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

    def __repr__(self):
        s = []
        s.append("state: ")
        for p in self.predicates:
            s.append(repr(p))
            s.append(" ; ")
        return "".join(s)

    @property
    def predicates(self):
        return self._predicates

    def set_predicates(self, new_predicates: Set):
        self._predicates = new_predicates

    def get_value(self):
        return 0


class CombinationState(State):
    def __init__(self, predicates: Set["up.model.fnode.Fnode"] = None, active_actions: "up.engines.ActionQueue" = None, current_time: int = None):
        super().__init__(predicates)
        self._active_actions = active_actions if active_actions else ActionQueue()
        self._current_time = current_time if current_time else 0

    def __eq__(self, other):
        if isinstance(other, State):
            return self.predicates == other.predicates \
                and self.active_actions == other.active_actions
        return False

    def __hash__(self):
        res = hash("")
        for p in self._predicates:
            res += hash(p)
        res += hash(self._active_actions)
        return res

    def __repr__(self):
        s = []
        s.append("state: ")
        s.append("predicates: ")
        for p in self.predicates:
            s.append(repr(p))
            s.append(" ; ")
        s.append("action queue: ")
        s.append(str(self.active_actions))
        s.append(" ; ")
        return "".join(s)

    @property
    def active_actions(self):
        return self._active_actions

    @property
    def current_time(self):
        return self._current_time

    def is_active_actions(self):
        if len(self.active_actions) == 0:
            return False
        return True

    def add_action(self, action: "up.engines.DurativeAction"):
        self.active_actions.add_action(QueueNode(action, action.duration.lower.int_constant_value()))

    def get_next_actions(self):
        return self.active_actions.get_next_actions()

    def update_actions_delta(self, delta: int):
        self.active_actions.update_delta(delta)

    def add_to_time(self, delta):
        self._current_time += delta


import heapq


class QueueNode:
    """ holds action and it's duration left """
    def __init__(self, action: "up.engines.Action", duration_left: int):
        self.action = action
        self.duration_left = duration_left

    def __hash__(self):
        res = hash("")
        res += hash(self.action)
        res += hash(self.duration_left)
        return res

    def __eq__(self, other):
        if isinstance(other, QueueNode):
            return self.action == other.action and self.duration_left == other.duration_left
        return False
    def __repr__(self):
        s = []
        s.append(f'({self.action.name},{str(self.duration_left)})')
        return "".join(s)

    def clone(self):
        new_node = QueueNode(self.action, self.duration_left)
        return new_node

    def __lt__(self, other):
        """ Compares two nodes based on the duration left"""
        return self.duration_left < other.duration_left


class ActionQueue:
    """
    Actions currently in execution and the remaining duration left for their execution
    """
    def __init__(self):
        self.data = []

    def __eq__(self, other):
        if isinstance(other, ActionQueue):
            return self.data == other.data
        return False

    def __hash__(self):
        res = hash("")
        for node in self.data:
            res += hash(node)
        return res

    def __repr__(self):
        s = []
        s.append("action queue: ")
        for node in self.data:
            s.append(str(node))
            s.append(" ; ")
        return "".join(s)

    def __len__(self):
        return len(self.data)

    def clone(self):
        new_action_queue = ActionQueue()
        new_action_queue.data = [node.clone() for node in self.data]
        return new_action_queue

    def add_action(self, node):
        heapq.heappush(self.data, node)

    def get_next_actions(self):
        """
        Get the actions that have the smallest duration left.
        There can be several actions that have the same duration left.
        """
        next_actions = []
        if self.data:
            min_duration = self.data[0].duration_left
            while self.data and self.data[0].duration_left == min_duration:
                node = heapq.heappop(self.data)
                next_actions.append(node.action)
            return min_duration, next_actions
        else:
            return -1, []

    def update_delta(self, delta: int):
        """ Extract delta from each of the actions in data: duration_left = duration_left - delta """
        for i in range(len(self.data)):
            self.data[i].duration_left -= delta
