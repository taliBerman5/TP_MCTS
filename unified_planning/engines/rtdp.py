import unified_planning as up
import math
import time
import random
from unified_planning.engines.utils import (
    create_init_stn,
    update_stn,
)
from collections import defaultdict

random.seed(10)
class RTDP:
    def __init__(self, mdp, root_state: "up.engines.state.State", search_depth: int):
        self._mdp = mdp
        self._root_state = root_state
        self._search_depth = search_depth
        self.V = defaultdict(lambda: 0.) # TODO:if the heuristic is not 0 these needs to ne changed to {}


    @property
    def mdp(self):
        return self._mdp

    @property
    def root_state(self):
        return self._root_state

    @property
    def search_depth(self):
        return self._search_depth


    def trial(self):
        """
        """
        state = self.root_state
        terminal = False

        while not terminal:
            action, action_value = self.evaluate(state)
            self.V[state] = action_value
            terminal, state, reward = self.mdp.step(state, action)


    def eval_action(self, state: "up.engines.State", action: "up.engines.Action"):
        # Heuristic value if the state is not stored in V table else V[state]

        _, _, reward = self.mdp.step(state, action)
        Q_s_a = reward + self.mdp.discount_factor # TODO: multiply be sum of probability function multiply by V or H

        return Q_s_a

    def evaluate(self, state: "up.engines.State"):
        best_a = -1
        best_value = -math.inf
        for action in self.mdp.legal_actions(state):
            Q_s_a = self.eval_action(state, action)
            if Q_s_a > best_value:
                best_a = action
                best_value = Q_s_a
        return best_a, best_value







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
    root_state = mdp.initial_state()

    history = []
    step = 0
    # for i in range(steps):
    while True:
        print(f"started step {step}")
        mcts = RTDP(mdp, root_state, search_depth)
        action = mcts.search(1)

        if action == -1:
            print("A valid plan is not found")
            break

        print(f"Current state is {root_state}")
        print(f"The chosen action is {action.name}")



        terminal, root_state, reward = mcts.mdp.step(root_state, action)


        # previous_STNNode = history[-1] if history else None
        history.append(action)


        if terminal:
            print(f"Current state is {root_state}")
            break

        step +=1
