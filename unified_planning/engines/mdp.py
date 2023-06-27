import unified_planning as up
import numpy as np
from unified_planning.exceptions import UPPreconditionDonHoldException
class MDP:
    def __init__(self, problem: "up.model.problem.Preoblem", discount_factor: float):
        self._problem = problem
        self._discount_factor = discount_factor

    @property
    def problem(self):
        return self._problem

    @property
    def discount_factor(self):
        return self._discount_factor

    def initial_state(self):
        """

        :return: the initial state of the problem
        """
        predicates = self.problem.initial_values
        pos_predicates = set([key for key, value in predicates.items() if value])
        return up.engines.State(pos_predicates)


    def is_terminal(self, state: "up.engines.state.State"):
        """
        Checks if all the goal predicates hold in the `state`

        :param state: checked state
        :return: True is the `state` is a terminal state, False otherwise
        """

        return set(self.problem.goals).issubset(state.predicates)


    def legal_actions(self, state: "up.engines.state.State"):
        """
        If the positive preconditions of an action are true in the state
        and the negative preconditions of the action are false in the state
        The action is considered legal for the state

        :param state: the current state of the system
        :return: the legal actions that can be preformed in the state `state`
        """
        legal_actions = []
        for action in self.problem.actions:
            if action.pos_precondition.issubset(state.predicates) and \
                    action.neg_precondition.isdisjoint(state.predicates):

                legal_actions.append(action)

        return legal_actions

    def step(self, state:"up.engines.State", action: "up.engines.action.Action"):
        """
               Apply the action to this state to produce the next state.
        """
        # Make sure it is legal to run the action in the state
        if not action.pos_preconditions.issubset(state.predicates):
            msg = f"Some of the positive preconditions of action {action.name} dont hold is the current state."
            raise UPPreconditionDonHoldException(msg)

        if not action.neg_preconditions.isdisjoint(state.predicates):
            msg = f"Some of the negative preconditions of action {action.name} dont hold is the current state."
            raise UPPreconditionDonHoldException(msg)

        reward = 0

        new_preds = set(state.predicates)
        new_preds |= set(action.add_effects)
        new_preds -= set(action.del_effects)

        add_predicates, del_predicates = self._apply_probabilistic_effects(state, action)
        new_preds |= add_predicates
        new_preds -= del_predicates
        next_state = up.engines.State(new_preds)
        return self.is_terminal(next_state), next_state, reward

    def _apply_probabilistic_effects(self, state:"up.engines.State", action: "up.engines.Action"):
        """

        :param action: draw the outcome of the probabilistic effects
        :return: the precicates that needs to be added and removed from the state
        """
        add_predicates = set()
        del_predicates = set()

        for pe in action.probabilistic_effects:
            prob_outcomes = pe.probability_function(self, None)
            index = np.random.choice(len(prob_outcomes), p=list(prob_outcomes.keys()))
            values = list(prob_outcomes.values())[index]
            for v in values:
                if values[v]:
                    add_predicates.add(v)
                else:
                    del_predicates.add(v)

        return add_predicates, del_predicates