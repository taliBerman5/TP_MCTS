import heapq
import math
import unified_planning as up
from typing import Dict
import numpy as np


class TRPG:

    def __init__(self, mdp: "up.engines.MDP", state: "up.engines.State", current_time: int):
        self.mdp = mdp
        self.negative = set(mdp.problem.initial_values.keys()).difference(state.predicates)
        self.positive = set(state.predicates)
        self.new_actions = []
        self.legal_probabilistic_actions = []
        self.deadline = self.mdp.deadline() if self.mdp.deadline() else math.inf
        self.current_time = current_time

    def get_heuristic(self, lower_bounds=None):
        """
        Calculates the heuristic based on the current state and time
        """
        t = self.current_time
        earliest = self.init_actions(lower_bounds)

        while t <= self.deadline and not self.mdp.problem.goals.issubset(self.positive):
            negative_eps = set(self.negative)
            positive_eps = set(self.positive)

            for action in self.legal_probabilistic_actions:
                perform = True
                if isinstance(action, up.engines.InstantaneousEndAction):
                    if earliest[action] <= t:
                        earliest[action] = t + action.start_action.duration.lower.int_constant_value()
                    else:
                        perform = False
                if perform:
                    self.add_probabilistic_effects(action, negative_eps, positive_eps)

            for action in self.new_actions[:]:

                # end action can occur only after `earliest[action]` time
                if isinstance(action, up.engines.InstantaneousEndAction):
                    if earliest[action] > t:
                        continue

                # Checks if the preconditions of the action are held
                legal = self.legal_action(action)

                if not legal:
                    continue

                # Sets the time when the end action can be executed
                if isinstance(action, up.engines.InstantaneousStartAction):
                    earliest[action.end_action] = min(earliest.get(action.end_action),
                                                      t + action.duration.lower.int_constant_value())

                # add the effects of the action to the next state
                self.add_effects(action, negative_eps, positive_eps)

                self.new_actions.remove(action)

                if action.probabilistic_effects:
                    self.legal_probabilistic_actions.append(action)
                    # The next time the end action can be executed is after the duration time
                    if isinstance(action, up.engines.InstantaneousEndAction):
                        earliest[action] = t + action.start_action.duration_int()

            # advance the time
            if len(negative_eps.difference(self.negative)) > 0 or len(positive_eps.difference(self.positive)) > 0:
                self.negative = negative_eps
                self.positive = positive_eps
            else:
                endpoints = [earliest.get(a) for a in earliest.keys() if self.legal_action(a) and a in self.new_actions]
                endpoints += [earliest.get(a) for a in earliest.keys() if a in self.legal_probabilistic_actions]
                if endpoints:
                    t = min(endpoints)
                else:
                    t = math.inf

        value = self.logistic_evaluate(t)
        return value

    def prob_evaluate(self, t):
        return 0.5 * (1 + (self.deadline - t) * 1.0 / self.deadline) if t <= self.deadline else 0

    def add_evaluate(self, t):
        return self.deadline - t + 10 if t <= self.deadline else 0

    def logistic_evaluate(self, t):
        if t > self.deadline:
            return 0
        if t == 0:
            return 1

        c = 1
        D_tag = self.deadline + c
        z1 = math.log(t/(D_tag - t))
        a1 = -0.5
        a0 = 1
        z2 = a1*z1 + a0
        p = 1/(1+math.exp(-z2))
        return p



    def add_probabilistic_effects(self, action, negative_eps, positive_eps):
        state = up.engines.State(positive_eps)
        add_predicates, del_predicates = self.mdp.apply_probabilistic_effects(state, action)
        negative_eps.update(del_predicates)
        positive_eps.update(add_predicates)

    def add_effects(self, action, negative_eps, positive_eps):
        negative_eps.update(action.del_effects)
        positive_eps.update(action.add_effects)
        self.add_probabilistic_effects(action, negative_eps, positive_eps)

    def init_actions(self, lower_bounds):
        """
        Init all actions into the new actions list
        ensures the end actions can be performed only after the start actions.

        :return: earliest - a dictionary containing the earliest time each end action can be executed
        """

        earliest = {}
        inExecution = self.mdp.problem.fluent_by_name('inExecution')

        for action in self.mdp.problem.actions:
            self.new_actions.append(action)

            # Makes sure end action can start only after the start action is performed
            if isinstance(action, up.engines.InstantaneousEndAction):
                action_object = self.mdp.problem.object_by_name(f'start-{action.name[4:]}')

                if not inExecution(action_object) in self.positive:
                    earliest[action] = math.inf
                elif lower_bounds is None:
                    earliest[action] = self.current_time
                else:
                    earliest[action] = lower_bounds[action]

                # earliest[action] = self.current_time if inExecution(action_object) in self.positive else math.inf

        return earliest

    def legal_action(self, action):
        return action.pos_preconditions.issubset(self.positive) and action.neg_preconditions.issubset(self.negative)

