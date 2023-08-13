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
        self.V = defaultdict(lambda: 0.)  # TODO:if the heuristic is not 0 these needs to ne changed to {}

    @property
    def mdp(self):
        return self._mdp

    @property
    def root_state(self):
        return self._root_state

    @property
    def search_depth(self):
        return self._search_depth

    def search(self, timeout):
        start_time = time.time()
        current_time = time.time()
        i = 0
        while current_time < start_time + timeout:
            self.trial()
            current_time = time.time()
            i += 1
        print(f'i = {i}')

        best_action, _ = self.evaluate(self.root_state)
        return best_action

    def trial(self):
        """
        """
        state = self.root_state
        terminal = False

        while not terminal:  # TODO: add another stopping criteria (number of steps or time)
            action, action_value = self.evaluate(state)
            self.V[state] = action_value
            terminal, state, reward = self.mdp.step(state, action)

    def eval_action(self, state: "up.engines.State", action: "up.engines.Action"):
        # Heuristic value if the state is not stored in V table else V[state]

        _, _, reward = self.mdp.step(state, action)
        trans = self.mdp.transition_function(state, action)
        nextV = 0
        for state, prob in trans:
            nextV += prob * self.V[state]

        Q_s_a = reward + self.mdp.discount_factor * nextV   # TODO: multiply be sum of probability function multiply by V or H
        if Q_s_a > 0:
            4
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


def plan(mdp: "up.engines.MDP", steps: int, search_depth: int):
    root_state = mdp.initial_state()

    rtdp = RTDP(mdp, root_state, search_depth)
    rtdp.search(1)
    step = 0
    history = []

    while True:
        print(f"started step {step}")
        rtdp = RTDP(mdp, root_state, search_depth)
        action = rtdp.search(1)

        terminal, root_state, reward = mdp.step(root_state, action)

        print(f"Current state is {root_state}")
        print(f"The chosen action is {action.name}")

        history.append(action)

        if terminal:
            print(f"Current state is {root_state}")
            break

        step += 1
