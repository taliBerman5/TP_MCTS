import unified_planning as up
from typing import List, Dict
from unified_planning.engines.utils import (
    update_stn,
)

class Node:
    def __init__(self):
        self._count = 0
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
    def __init__(self, state: "up.engines.State", depth: int, possible_actions: List["up.engines.Action"], stn: "up.plans.stn.STNPlan", parent: "up.engines.ANode"=None, previous_chosen_action_node: "up.plans.stn.STNPlanNode" = None):
        super().__init__()
        self._state = state
        self._depth = depth
        self._parent = parent
        self._children: Dict["up.engines.Action", "up.engines.ANode"] = {}
        self._possible_actions = possible_actions
        self._add_children(stn, previous_chosen_action_node)

    def __repr__(self):
        s = "state Node; depth: %d; children: %d; visits: %d; reward: %f" % (self.depth, len(self.children), self.count, self.value)
        return s

    @property
    def state(self):
        return self._state

    @property
    def depth(self):
        return self._depth

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    @property
    def possible_actions(self):
        return self._possible_actions

    def remove_action(self, action: "up.engines.Action"):
        if action in self._possible_actions:
            self._possible_actions.remove(action)

    def _add_children(self, stn: "up.plans.stn.STNPlan", previous_chosen_action_node: "up.plans.stn.STNPlanNode" = None):
        """
        Adds to the SNode the possible actions as children.
        If a specific children is not consistent (adding the constaints of the action to the `stn`)
        then the action is not possible in this SNode

        :param stn: The STN from the previous node
        :param previous_chosen_action_node: the action chosen in the last search step
        :return:
        """
        not_consistent = []
        for action in self.possible_actions:
            child = ANode(action, stn.clone(), self, previous_chosen_action_node)

            if child.is_consistent():
                self.children[action] = child
            else:
                not_consistent.append(action)

        for a in not_consistent:
            self.possible_actions.remove(a)



class ANode(Node):
    def __init__(self, action: "up.engines.action.Action", stn: "up.plans.stn.STNPlan", parent: "up.engines.node.SNode"=None, previous_chosen_action_node: "up.plans.stn.STNPlanNode" = None):
        super().__init__()
        self._action = action
        self._parent = parent
        self._children: Dict["up.engines.State","up.engines.node.SNode"] = {}
        self._stn = stn

        self._add_constraints(previous_chosen_action_node)  # Adds the action constraints to the STN

    def __repr__(self):
        s = "action Node; children: %d; visits: %d; reward: %f" % (len(self.children), self.count, self.value)
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

    def add_child(self, child_node: "up.engines.SNode"):
        self._children[child_node.state] = child_node

    def isLeaf(self):
        return self.children

    @property
    def stn(self):
        return self._stn

    def is_consistent(self):
        return self._stn.is_consistent()

    def _add_constraints(self, previous_chosen_action_node: "up.plans.stn.STNPlanNode" = None):
        """

        add constraints to the STN according to this `self` action
        If this parent node is not the root of this tree,
        the previous node is the parent of the parent (last action in the searching tree)

        Otherwise, the previous node is the last chosen action (from the previous search step) if exists (not the first round)

        :param previous_chosen_action_node: The action node chosen in the previous step
        :return:
        """
        previous_action = self.parent.parent
        previous_node = previous_chosen_action_node

        if previous_action:
            previous_action = previous_action.action
            if isinstance(previous_action, up.engines.action.InstantaneousEndAction):
                previous_node = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.END, up.plans.plan.ActionInstance(previous_action, ()))
            else:
                previous_node = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.START, up.plans.plan.ActionInstance(previous_action, ()))

        update_stn(self.stn, self.action, previous_node)











