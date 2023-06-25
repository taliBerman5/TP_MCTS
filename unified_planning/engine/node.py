import unified_planning as up
from typing import List


class Node:
    def __init__(self):
        self._count = 1
        self._value = 0.0

    def __repr__(self):
        s = "Node; visits: %d; value: %f" % (self.count, self.value)
        return s

    @property
    def count(self):
        return self._count

    @property
    def value(self):
        return self._value

    def update(self, reward):
        self._value += reward
        self._count += 1

class SNode(Node):
    def __init__(self, state: "up.engine.State", possible_actions: List["up.engine.Action"], parent: "up.engine.ANode"=None):
        super().__init__()
        self._state = state
        self._parent = parent
        self._children: List["up.engine.node.ANode"] = []
        self._possible_actions = possible_actions

    def __repr__(self):
        s = "Node; children: %d; visits: %d; reward: %f" % (len(self.children), self.count, self.value)
        return s

    @property
    def state(self):
        return self._state

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    @property
    def possible_actions(self):
        return self._possible_actions

    def remove_action(self, action: "up.engine.Action"):
        if action in self._possible_actions:
            self._possible_actions.remove(action)

    def add_child(self, child_action: "up.engine.Action"):
        child = ANode(child_action, self)
        self.children.append(child)

    def isLeaf(self):
        return self.children



class ANode(Node):
    def __init__(self, action: "up.engine.action.Action", parent: "up.engine.node.SNode"=None):
        super().__init__()
        self._action = action
        self._parent = parent
        self._children: List["up.engine.node.SNode"] = []

    def __repr__(self):
        s = "Node; children: %d; visits: %d; reward: %f" % (len(self.children), self.count, self.value)
        return s

    @property
    def action(self):
        return self._action

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    def add_child(self, child_state: "up.engine.State", legal_action: List["up.engine.Action"]):
        child = SNode(child_state, legal_action, self)
        self._children.append(child)





