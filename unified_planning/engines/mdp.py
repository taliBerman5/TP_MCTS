from typing import List

import unified_planning as up
import numpy as np
from unified_planning.exceptions import UPPreconditionDonHoldException
from itertools import product


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

    def deadline(self):
        return self.problem.deadline

    def initial_state(self):
        """

        :return: the initial state of the problem
        """
        predicates = self.problem.initial_values
        pos_predicates = set([key for key, value in predicates.items() if value.bool_constant_value()])
        return up.engines.State(pos_predicates)

    def is_terminal(self, state: "up.engines.state.State"):
        """
        Checks if all the goal predicates hold in the `state`

        :param state: checked state
        :return: True is the `state` is a terminal state, False otherwise
        """

        return self.problem.goals.issubset(state.predicates)

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
            if isinstance(action, up.engines.NoOpAction):
               continue
            if action.pos_preconditions.issubset(state.predicates) and \
                    action.neg_preconditions.isdisjoint(state.predicates):
                if self.check_action_relevant(state, action):
                    # prone action that don't add new effects
                    legal_actions.append(action)

        return legal_actions

    def update_predicate(self, state: "up.engines.State", new_preds: set, action: "up.engines.action.Action"):
        new_preds |= action.add_effects
        new_preds -= action.del_effects

        add_predicates, del_predicates = self.apply_probabilistic_effects(state, action)
        new_preds |= add_predicates
        new_preds -= del_predicates

        return new_preds

    def step(self, state: "up.engines.State", action: "up.engines.action.Action"):
        """
               Apply the action to this state to produce the next state.
        """
        new_preds = set(state.predicates)
        new_preds = self.update_predicate(state, new_preds, action)
        next_state = up.engines.State(new_preds)

        terminal = self.is_terminal(next_state)
        relevant_reward = 0
        # relevant_reward = self.check_action_relevant(state, action)

        # common = len(self.problem.goals.intersection(state.predicates))
        # reward = 100 if terminal else 2 ** (common - len(self.problem.goals))

        # reward = 10 if terminal else relevant_reward
        reward = 1 if terminal else relevant_reward

        return terminal, next_state, reward

    def check_action_relevant(self, state: "up.engines.State", action):
        if not isinstance(action, up.engines.InstantaneousStartAction):
            return True #-1

        add = action.add_effects.copy()
        # Remove inExecution - this is not considered new effect
        for add_effect in add.copy():
            if add_effect._content.payload == self.problem.fluent_by_name('inExecution'):
                add.remove(add_effect)

        not_relevant = add.issubset(state.predicates)
        not_relevant &= action.del_effects.isdisjoint(state.predicates)
        not_relevant &= action.end_action.add_effects.issubset(state.predicates)
        not_relevant &= action.end_action.del_effects.isdisjoint(state.predicates)
        for pe in action.end_action.probabilistic_effects:
            not_relevant = not_relevant & set(pe.fluents).issubset(state.predicates)

        if not_relevant:
            return False #-50
        return True #-1

    def probabilistic_effects(self, prob_outcomes, index):
        """ Gets the add and delete effect of the prob_outcome index effect"""
        add_predicates = set()
        del_predicates = set()

        probability = list(prob_outcomes.keys())[index]
        values = list(prob_outcomes.values())[index]
        for v in values:
            if values[v]:
                add_predicates.add(v)
            else:
                del_predicates.add(v)

        return probability, add_predicates, del_predicates

    def apply_probabilistic_effects(self, state: "up.engines.State", action: "up.engines.Action"):
        """

        :param action: draw the outcome of the probabilistic effects
        :return: the precicates that needs to be added and removed from the state
        """
        add_predicates = set()
        del_predicates = set()

        for pe in action.probabilistic_effects:
            prob_outcomes = pe.probability_function(state, None)
            if prob_outcomes:
                index = np.random.choice(len(prob_outcomes), p=list(prob_outcomes.keys()))

                _, add, delete = self.probabilistic_effects(prob_outcomes, index)

                add_predicates.update(add)
                del_predicates.update(delete)

        return add_predicates, del_predicates


class combinationMDP(MDP):
    def __init__(self, problem: "up.model.problem.Problem", discount_factor: float):
        super().__init__(problem, discount_factor)

    def initial_state(self):
        """

        :return: the initial state of the problem
        """
        predicates = self.problem.initial_values
        pos_predicates = set([key for key, value in predicates.items() if value.bool_constant_value()])
        return up.engines.CombinationState(pos_predicates)

    def is_terminal(self, state: "up.engines.state.CombinationState"):
        """
        Checks if all the goal predicates hold in the `state`
        and there are no active actions

        :param state: checked state
        :return: True is the `state` is a terminal state, False otherwise
        """
        return super().is_terminal(state) #and not state.is_active_actions  TODO: decide if we allow or not active actions

    def step(self, state: "up.engines.CombinationState", action: "up.engines.action.Action"):
        """
               Apply the action to this state to produce the next state.

               If the action is:

               - Instantaneous: the predicates are updated according to the action effects

               - Durative: adds the action to the active action and adds inExecution predicate
               - Combination: adds each of the durative actions to the active action and add inExecution predicates
               - No-op: nothing is added.

               for each Durative, Combination, No-op:
                   Finds the action(s) with the shortest duration left,
                   updates the predicates according to this action(s)
                   extracts delta from the rest of the active actions

        """

        new_preds = set(state.predicates)
        new_active_actions = state.active_actions.clone()
        current_time = state.current_time

        if isinstance(action, up.engines.InstantaneousAction):
            actions_to_perform = [action]

        # Deals with no-op, durative actions and combination actions
        else:
            if isinstance(action, up.engines.DurativeAction):
                new_active_actions.add_action(up.engines.QueueNode(action, action.duration.lower.int_constant_value()))
                new_preds |= action.inExecution

            elif isinstance(action, up.engines.CombinationAction):
                for a in action.actions:
                    new_active_actions.add_action(up.engines.QueueNode(a, a.duration.lower.int_constant_value()))

                new_preds |= action.inExecution

            delta, actions_to_perform = new_active_actions.get_next_actions()

            if delta != -1:
                new_active_actions.update_delta(delta)
                current_time += delta

        # update the predicates according to the actions needs to be preformed
        for a in actions_to_perform:
            new_preds = super().update_predicate(state, new_preds, a)

        next_state = up.engines.CombinationState(new_preds, new_active_actions, current_time)

        terminal = self.is_terminal(next_state)

        # common = len(self.problem.goals.intersection(state.predicates))
        # reward = 100 if terminal else 2 ** (common - len(self.problem.goals))
        reward = 10 if terminal else -1

        return terminal, next_state, reward

    def transition_function(self, state: "up.engines.State", action: "up.engines.Action"):

        new_preds_init = set(state.predicates)
        new_active_actions = state.active_actions.clone()
        current_time = state.current_time

        if isinstance(action, up.engines.InstantaneousAction):
            new_preds_init |= action.add_effects
            new_preds_init -= action.del_effects
            actions_to_perform = [action]

        # Deals with no-op, durative actions and combination actions
        else:
            if isinstance(action, up.engines.DurativeAction):
                new_active_actions.add_action(up.engines.QueueNode(action, action.duration.lower.int_constant_value()))
                new_preds_init |= action.inExecution

            elif isinstance(action, up.engines.CombinationAction):
                for a in action.actions:
                    new_active_actions.add_action(up.engines.QueueNode(a, a.duration.lower.int_constant_value()))

                new_preds_init |= action.inExecution

            delta, actions_to_perform = new_active_actions.get_next_actions()

            for a in actions_to_perform:
                new_preds_init |= a.add_effects
                new_preds_init -= a.del_effects

            if delta != -1:
                new_active_actions.update_delta(delta)
                current_time += delta

        probs = self.all_probabilistic_effects(state, actions_to_perform)
        transition = []
        for prob in probs:
            new_preds = new_preds_init.copy()
            new_preds |= prob['add']
            new_preds -= prob['delete']
            next_state = up.engines.CombinationState(new_preds, new_active_actions, current_time)
            transition.append((next_state, prob['probability']))

        return transition

    def all_probabilistic_effects(self, state: "up.engines.State", actions: List["up.engines.Action"]):
        pe_length = []
        pe_outcomes = []

        # Get the length of each probabilistic effect greater then 0
        for action in actions:
            for pe in action.probabilistic_effects:
                prob_outcomes = pe.probability_function(state, None)
                if prob_outcomes:
                    pe_outcomes.append(prob_outcomes)
                    pe_length.append(len(prob_outcomes))

        # holds all combination of indexes
        series = list(product(*(range(x) for x in pe_length)))

        effects = []
        for s in series:
            add_predicates = set()
            del_predicates = set()
            probability = 1
            for i, p in enumerate(pe_outcomes):
                prob, add, delete = self.probabilistic_effects(p, s[i])

                add_predicates.update(add)
                del_predicates.update(delete)
                probability *= prob
            effects.append({"probability": probability, "add": add_predicates, 'delete': del_predicates})

        return effects

    def legal_actions(self, state: "up.engines.state.CombinationState"):
        """
        If the positive preconditions of an action are true in the state
        and the negative preconditions of the action are false in the state
        The action is considered legal for the state

        :param state: the current state of the system
        :return: the legal actions that can be preformed in the state `state`
        """
        legal_actions = super().legal_actions(state)
        if state.active_actions.data:
            legal_actions.append(self.problem.action_by_name('noop'))
        return legal_actions