import unified_planning as up
import math
import time
import random
from collections import defaultdict
from typing import List
from unified_planning.engines.utils import (
    create_init_stn,
    update_stn,
)


class MCTS:
    def __init__(self, mdp, root_state: "up.engines.state.State", search_depth: int, exploration_constant: float,
                 stn: "up.plans.stn.STNPlan"):
        self._mdp = mdp
        self._root_state = root_state
        self._search_depth = search_depth
        self._exploration_constant = exploration_constant
        self._stn = stn

    @property
    def mdp(self):
        return self._mdp

    @property
    def root_state(self):
        return self._root_state

    @property
    def search_depth(self):
        return self._search_depth

    @property
    def exploration_constant(self):
        return self._exploration_constant

    @property
    def stn(self):
        return self._stn

    def mcts(self, timeout=1):
        """
        Execute the MCTS algorithm from the initial state given, with timeout in seconds
        """

        root_node = self.create_Snode(self.root_state, 0, self._stn)

        start_time = time.time()
        current_time = time.time()
        while current_time < start_time + timeout:
            self.selection(root_node)
            current_time = time.time()

        return self.best_action(root_node)

    def create_Snode(self, state: "up.engines.State", depth: int, stn: "up.plans.stn.STNPlan",
                     parent: "up.engines.ANode" = None):
        """ Create a new Snode for the state `state` with parent `parent`"""
        return up.engines.SNode(state, depth, self.mdp.legal_actions(state), stn, parent)

    def selection_while(self, snode: "up.engines.Snode"):

        terminal = False
        consistent = False
        action = -1

        # Stop if the search depth is reached or
        # the there are no possible actions to take so the plan remains consistent
        while snode.depth < self.search_depth and len(snode.possible_actions) > 0:

            explore_constant = self.exploration_constant

            while not consistent:
                action = self.uct(snode, explore_constant)
                consistent = snode.children[action].is_consistent()

                if len(snode.possible_actions) > 0:
                    return

            terminal, next_state, reward = self.mdp.step(snode.state, action)

            anode = snode.children[action]

            if not terminal:
                snodes = anode.children
                if next_state in snodes:
                    reward += self.mdp.discount_factor * self.selection(snodes[next_state])

                else:
                    reward += self.mdp.discount_factor * self.simulate(snodes[next_state])
                    next_snode = self.create_Snode(next_state, snode.depth + 1, snode.parent.stn)

                    anode.add_child(next_snode)

            snode.update(reward)
            anode.update(reward)

        return reward

    def selection(self, snode: "up.engines.Snode"):

        if snode.depth > self.search_depth or len(snode.possible_actions) == 0:
            # Stop if the search depth is reached or
            # the there are no possible actions to take so the plan remains consistent
            return 0

        explore_constant = self.exploration_constant

        # Choose a consistent action
        action = self.uct(snode, explore_constant)

        terminal, next_state, reward = self.mdp.step(snode.state, action)

        anode = snode.children[action]
        if not terminal:
            snodes = anode.children
            if next_state in snodes:
                reward += self.mdp.discount_factor * self.selection(snodes[next_state])

            else:
                reward += self.mdp.discount_factor * self.simulate(next_state)
                next_snode = self.create_Snode(next_state, snode.depth + 1, anode.stn, anode)
                anode.add_child(next_snode)

        snode.update(reward)
        anode.update(reward)

        return reward

    def default_policy(self, state: "up.engines.State"):
        """ Choose a random action. Heustics can be used here to improve simulations. """
        return random.choice(self.mdp.legal_actions(state))

    def simulate(self, state):
        """ Simulate until a terminal state """
        cumulative_reward = 0.0
        depth = 0
        terminal = False

        while not terminal and depth < self.search_depth and len(self.mdp.legal_actions(state)) > 0:
            # Choose an action to execute
            action = self.default_policy(state)

            # Execute the action
            (terminal, next_state, reward) = self.mdp.step(state, action)

            # Discount the reward
            cumulative_reward += pow(self.mdp.discount_factor, depth) * reward
            depth += 1

            state = next_state

        return cumulative_reward

    def uct(self, snode: "up.engines.Snode", explore_constant: float):  # TODO: need to check to the uct logic
        anodes = snode.children
        best_ub = -float('inf')
        best_action = -1
        possible_actions = snode.possible_actions
        for action in possible_actions:
            if anodes[action].count == 0:
                return action

            ub = anodes[action].value + explore_constant * math.sqrt(math.log(snode.count + 1) / anodes[action].count)
            if ub > best_ub:
                best_ub = ub
                best_action = action

        assert best_action != -1
        return best_action

    def best_action(self, root_node: "up.engines.SNode"):
        """

        :param root_node: the root node of the MCTS tree
        :return: returns the best action for the `root_node`
        """
        anodes = root_node.children
        aStart_value = float("-inf")
        aStar = -1

        for action in root_node.possible_actions:
            if anodes[action].value > aStart_value:
                aStart_value = anodes[action].value
                aStar = action

        return aStar


def plan(mdp: "up.engines.MDP", steps: int, search_depth: int, exploration_constant: float):
    stn = create_init_stn(mdp)
    root_state = mdp.initial_state()

    history = []

    for i in range(steps):
        mcts = MCTS(mdp, root_state, search_depth, exploration_constant, stn)
        action = mcts.mcts()

        terminal, root_state, reward = mcts.mdp.step(root_state, action)

        previous_action = history[-1] if history else None
        action_node = update_stn(stn, action, previous_action)  # TODO: check if the stn and history gets updated
        history.append(action_node)
        assert stn.is_consistent

        if terminal:
            break
