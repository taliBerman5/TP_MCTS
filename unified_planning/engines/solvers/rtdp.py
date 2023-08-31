import unified_planning as up
import math
import time
import random
from collections import defaultdict

random.seed(10)


class RTDP:
    def __init__(self, mdp, split_mdp, root_state: "up.engines.state.State", search_depth: int):
        self._mdp = mdp
        self._root_state = root_state
        self._search_depth = search_depth
        self.V = {}
        self.current_time = 0
        self.split_mdp = split_mdp

    @property
    def mdp(self):
        return self._mdp

    @property
    def root_state(self):
        return self._root_state

    @property
    def search_depth(self):
        return self._search_depth

    def update_root(self, root_state):
        self._root_state = root_state

    def search(self, timeout):
        start_time = time.time()
        current_time = time.time()
        i = 0
        while current_time < start_time + timeout:
            self.trial(timeout, start_time)
            current_time = time.time()

        best_action, _ = self.evaluate(self.root_state)
        return best_action

    def trial(self, timeout, start_time):
        """
        """
        state = self.root_state
        terminal = False
        depth = 0
        while (not terminal) and (depth < self.search_depth):  # TODO: add another stopping criteria (number of steps or time)
            action, action_value = self.evaluate(state)
            self.V[state] = action_value
            terminal, state, reward = self.mdp.step(state, action)
            depth += 1

            current_time = time.time()
            if current_time > start_time + timeout:
                return

    def eval_action(self, state: "up.engines.State", action: "up.engines.Action"):
        # Heuristic value if the state is not stored in V table else V[state]

        _, _, reward = self.mdp.step(state, action)
        trans = self.mdp.transition_function(state, action)
        nextV = 0
        for state, prob in trans:
            if state in self.V:
                value = self.V[state]
            else:
                value = self.heuristic(state)
            nextV += prob * value

        Q_s_a = reward + self.mdp.discount_factor * nextV   # TODO: multiply be sum of probability function multiply by V or H
        return Q_s_a

    def evaluate(self, state: "up.engines.State"):
        best_a = []
        best_value = -math.inf
        for action in self.mdp.legal_actions(state):
            Q_s_a = self.eval_action(state, action)
            if Q_s_a > best_value:
                best_a = [action]
                best_value = Q_s_a
            elif Q_s_a == best_value:
                best_a.append(action)
        best_a = random.choice(best_a)
        return best_a, best_value

    def heuristic(self, state: "up.engines.State"):
        current_time = 0
        if isinstance(state, up.engines.CombinationState):
            current_time = state.current_time
        h = up.engines.heuristics.TRPG(self.split_mdp, state, current_time)
        return h.get_heuristic()


def plan(mdp: "up.engines.MDP", split_mdp: "up.engines.MDP", steps: int, search_depth: int):
    root_state = mdp.initial_state()

    step = 0
    history = []
    rtdp = RTDP(mdp, split_mdp, root_state, search_depth)

    while True:
        print(f"started step {step}")
        action = rtdp.search(40)

        terminal, root_state, reward = mdp.step(root_state, action)

        print(f"The chosen action is {action.name}")
        print(f"Current state is {root_state}")

        rtdp.update_root(root_state)
        print(f'current time = {root_state.current_time}')

        history.append(action)

        if terminal:
            print(f"Current state is {root_state}")
            break

        step += 1
