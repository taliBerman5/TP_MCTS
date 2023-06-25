import unified_planning as up
import math
import time
import random
from collections import defaultdict


class MCTS:
    def __init__(self, mdp, root_state: "up.engine.state.State"):
        self.mdp = mdp
        self.root_state = root_state

    """
    Execute the MCTS algorithm from the initial state given, with timeout in seconds
    """

    def mcts(self, timeout=1):
        root_node = self.create_root_node()

        start_time = time.time()
        current_time = time.time()
        while current_time < start_time + timeout:

            self.selection(root_node)

            # Find a state node to expand
            selected_node = root_node.select()
            if not self.mdp.is_terminal(selected_node):
                child = selected_node.expand()
                reward = self.simulate(child)
                selected_node.back_propagate(reward, child)

            current_time = time.time()

        return root_node

    def create_root_node(self):
        """ Create a root node representing an initial state """
        return up.engine.SNode(self.root_state)


    def selection(self, snode: "up.engine.Snode"):
        explore_constant = self.mdp.exploration_constant
        action = self.uct(snode, explore_constant)




    """ Simulate until a terminal state """

    def simulate(self, node):
        state = node.state
        cumulative_reward = 0.0
        depth = 0
        while not self.mdp.is_terminal(state):
            # Choose an action to execute
            action = self.choose(state)

            # Execute the action
            (next_state, reward) = self.mdp.execute(state, action)

            # Discount the reward
            cumulative_reward += pow(self.mdp.get_discount_factor(), depth) * reward
            depth += 1

            state = next_state

        return cumulative_reward

    def uct(self, snode: "up.engine.Snode", explore_constant: float): #TODO: need to check to the uct logic
        anodes = snode.children
        best_ub = float('inf')
        best_action = -1
        possible_actions = snode.possible_actions
        for action in possible_actions:
            if anodes[action].count == 0:
                return action

            ub = anodes[action].value + explore_constant * math.sqrt(math.log(snode.count + 1) / anodes[action].count)
            if ub > best_ub:
                best_action = ub
                best_action = action

        assert best_action != -1
        return best_action




