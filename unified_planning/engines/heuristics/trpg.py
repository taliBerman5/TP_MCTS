import heapq
import math
import unified_planning as up
from typing import Dict


class TRPG:

    def __init__(self, mdp: "up.engines.MDP", state: "up.engines.State", current_time: int):
        self.mdp = mdp
        self.negative = set(mdp.problem.initial_values.keys()).difference(state.predicates)
        self.positive = set(state.predicates)
        self.new_actions = []
        self.deadline = self.mdp.deadline() if self.mdp.deadline() else math.inf
        self.current_time = current_time
        self.delayed_effects = []

    def get_heuristic(self):

        t = self.current_time

        earliest = self.init_actions()

        while t < self.deadline and not self.mdp.problem.goals.issubset(self.positive):
            negative_eps = set(self.negative)
            positive_eps = set(self.positive)

            add_delayed_effects = self.get_next_delayed_effects(t)
            for add_predicates, del_predicates in add_delayed_effects:
                positive_eps.update(add_predicates)
                negative_eps.update(del_predicates)


            # TODO: check it is not missing any action when removing a legal action
            for action in self.new_actions[:]:

                # end action can occur only after `earliest[action]` time
                if isinstance(action, up.engines.InstantaneousEndAction):
                    if earliest[action] > t:
                        continue

                # Checks if the preconditions of the action are held
                legal = self.legal_action(action)

                # Sets the time when the end action can be executed
                if isinstance(action, up.engines.InstantaneousStartAction) and legal:
                    # TODO: check if the end_action in the dictionary is the same as the one inserted at the first loop
                    # TODO: check if the duration.lower is int
                    earliest[action.end_action] = min(earliest.get(action.end_action), t + action.duration.lower.int_constant_value())

                # add the effects of the action to the next state
                if legal:
                    self.new_actions.remove(action)
                    self.add_effects(t, action, negative_eps, positive_eps)

            if len(negative_eps.difference(self.negative)) > 0 or len(positive_eps.difference(self.positive)) > 0:
                self.negative = negative_eps
                self.positive = positive_eps
            else:
                endpoints = [earliest.get(a) for a in earliest.keys() if self.legal_action(a) and a in self.new_actions]
                delayed = [d.delayed_time for d in self.delayed_effects]
                combined = delayed + endpoints
                if combined:
                    t = min(combined)  # TODO: check
                else:
                    t = math.inf

        return t

    def add_effects(self, t, action, negative_eps, positive_eps):
        negative_eps.update(action.del_effects)
        positive_eps.update(action.add_effects)
        self.add_delayed_effects(action, t)

    def init_actions(self):
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
                earliest[action] = self.current_time if inExecution(action_object) in self.positive else math.inf

        return earliest

    def legal_action(self, action):
        return action.pos_preconditions.issubset(self.positive) and action.neg_preconditions.issubset(self.negative)

    def add_delayed_effects(self, action, t):
        for pe in action.probabilistic_effects:
            state = up.engines.State(self.positive)
            prob_outcomes = pe.probability_function(state, None)
            if prob_outcomes:
                for i in range(len(prob_outcomes)):
                    probability = list(prob_outcomes.keys())[i]
                    effects = list(prob_outcomes.values())[i]
                    delayed_time = action.start_action.duration.lower.int_constant_value() / probability + t

                    node = DelayedEffect(effects, delayed_time)
                    heapq.heappush(self.delayed_effects, node)

    def get_next_delayed_effects(self, t):
        next_effects = []
        if self.delayed_effects:
            min_t = self.delayed_effects[0].delayed_time
            if min_t > t:
                return []
            while self.delayed_effects and self.delayed_effects[0].delayed_time == min_t:
                node = heapq.heappop(self.delayed_effects)
                next_effects.append(node.effects)
            return next_effects
        else:
            return []


class DelayedEffect:
    """ holds effect and the earliest time it could be applied """

    def __init__(self, effects: Dict, delayed_time: int):
        self.effects = self.init_effects(effects)
        self.delayed_time = delayed_time

    def __hash__(self):
        res = hash("")
        res += hash(self.effects)
        res += hash(self.delayed_time)
        return res

    def __repr__(self):
        s = []
        s.append(f'({self.effects},{str(self.delayed_time)})')
        return "".join(s)

    def __lt__(self, other):
        """ Compares two nodes based on the delayed time """
        return self.delayed_time < other.delayed_time

    def init_effects(self, effects):
        add_predicates = set()
        del_predicates = set()
        for e in effects:
            if effects[e]:
                add_predicates.add(e)
            else:
                del_predicates.add(e)

        return add_predicates, del_predicates
