import math

import unified_planning as up
from typing import List, Dict
from unified_planning.shortcuts import *
from unified_planning.engines.utils import (
    update_stn,
)
from unified_planning.engines.linked_list import LinkedList


class Node:
    def __init__(self, isInterval=False):
        if isInterval:
            self._linkList = LinkedList()
        else:
            self._value = 0.0
        self._count = 0.0
        self._isInterval = isInterval


    def __repr__(self):
        s = "Node; visits: %d; value: %f" % (self.count, self.value)
        return s

    @property
    def count(self):
        return self._count

    @property
    def isInterval(self):
        return self._isInterval

    @property
    def value(self):
        if self._isInterval:
            return self._linkList.max_value / self.count
        return self._value

    def interval_value(self, lower, upper):
        return self._linkList.interval_value(lower, upper)


    def max_interval(self):
        if self._isInterval:
            return self._linkList.max_interval

    def update(self, reward, add_node: "LinkedListNode" = None):
        self._count += 1
        if add_node is None:
            self._value = (self._value * self._count + reward) / (self._count + 1)
        else:
            return self._linkList.update(add_node)



class SNode(Node):
    """ State node """

    def __init__(self, state: "up.engines.State", depth: int, possible_actions: List["up.engines.Action"],
                 parent: "up.engines.ANode" = None):
        super().__init__()
        self._state = state
        self._depth = depth
        self._parent = parent
        self._possible_actions = possible_actions
        self._children: Dict["up.engines.Action", "up.engines.ANode"] = {}
        self._add_children()

    def __repr__(self):
        s = "state Node; depth: %d; children: %d; visits: %d; reward: %f" % (
            self.depth, len(self.children), self.count, self.value)
        return s

    @property
    def state(self):
        return self._state

    @property
    def depth(self):
        return self._depth

    def set_depth(self, depth):
        self._depth = depth

    @property
    def parent(self):
        return self._parent

    @property
    def possible_actions(self):
        return self._possible_actions

    @property
    def children(self):
        return self._children

    def _add_children(self):
        """
        Adds to the SNode the possible actions as children.

        :param previous_chosen_action_node: the action chosen in the last search step
        """
        for action in self.possible_actions:
            self.children[action] = ANode(action, self)

    def max_update(self):
        max_v = -math.inf
        for child in self.children.values():
           if child.count > 0 and child.value > max_v:
                max_v = child.value
        self._value = max_v
        self._count += 1
        return max_v


class C_SNode(Node):
    """ State node with consistency STN check """

    def __init__(self, state: "up.engines.State", depth: int, possible_actions: List["up.engines.Action"],
                 stn: "up.plans.stn.STNPlan", parent: "up.engines.ANode" = None,
                 previous_chosen_action_node: "up.plans.stn.STNPlanNode" = None, isInterval=False):
        super().__init__(isInterval)
        self._state = state
        self._depth = depth
        self._parent = parent
        self._children: Dict["up.engines.Action", "up.engines.C_ANode"] = {}
        self._possible_actions = possible_actions
        self._add_children(stn, previous_chosen_action_node)

    def __repr__(self):
        s = "state Node; depth: %d; children: %d; visits: %d; reward: %f" % (
            self.depth, len(self.children), self.count, self.value)
        return s

    @property
    def state(self):
        return self._state

    @property
    def depth(self):
        return self._depth

    def set_depth(self, depth):
        self._depth = depth

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

    def _add_children(self, stn: "up.plans.stn.STNPlan",
                      previous_chosen_action_node: "up.plans.stn.STNPlanNode" = None):
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
            child = C_ANode(action, stn.clone(), self, previous_chosen_action_node, isInterval=self.isInterval)

            if child.is_consistent():
                self.children[action] = child
            else:
                not_consistent.append(action)

        for a in not_consistent:
            self.possible_actions.remove(a)

    def max_update(self, node=None):
        self._count += 1
        if node is None:  # TODO: maybe change to if self.isInterval
            return self.max_update_wo_interval()
        else:
            return self.max_update_interval(node)

    def max_update_wo_interval(self):
        max_v = -math.inf
        for child in self.children.values():
           if child.count > 0 and child.value > max_v:
                max_v = child.value
        self._value = max_v
        return max_v

    def max_update_interval(self, node):
        #TODO: is it ok to do max between the new value and the current value or should i go over all the children
        update_node = self._linkList.update(node, type='Max')
        return update_node


class ANode(Node):
    """ Action node """

    def __init__(self, action: "up.engines.action.Action",
                 parent: "up.engines.node.SNode" = None):
        super().__init__()
        self._action = action
        self._parent = parent
        self._children: Dict["up.engines.State", "up.engines.node.SNode"] = {}

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


class C_ANode(Node):
    """ Action node with consistency STN check """

    def __init__(self, action: "up.engines.action.Action", stn: "up.plans.stn.STNPlan",
                 parent: "up.engines.node.C_SNode" = None,
                 previous_chosen_action_node: "up.plans.stn.STNPlanNode" = None, isInterval = False):
        super().__init__(isInterval)
        self._action = action
        self._parent = parent
        self._children: Dict["up.engines.State", "up.engines.node.SNode"] = {}
        self._stn = stn
        self._STNNode = self._add_constraints(previous_chosen_action_node)

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

    @property
    def STNNode(self):
        return self._STNNode

    def add_child(self, child_node: "up.engines.SNode"):
        self._children[child_node.state] = child_node

    def isLeaf(self):
        return self.children

    @property
    def stn(self):
        return self._stn

    @property
    def STNNode(self):
        return self._STNNode

    def is_consistent(self):
        return self._stn.is_consistent()

    def _add_constraints(self, previous_chosen_action_node: "up.plans.stn.STNPlanNode" = None):
        """

        add constraints to the STN according to this `self` action
        If this parent node is not the root of this tree,
        the previous node is the parent of the parent (last action in the searching tree)

        Otherwise, the previous node is the last chosen action (from the previous search step) if exists (not the first round)

        :param previous_chosen_action_node: The action node chosen in the previous step
        :return: The added STN node to the STN
        """
        previous_action = self.parent.parent
        previous_node = previous_chosen_action_node

        if previous_action:
            previous_node = previous_action.STNNode

        return update_stn(self.stn, self.action, previous_node)
