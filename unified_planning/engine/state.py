import unified_planning as up
from typing import Tuple, List, Set
from unified_planning.exceptions import UPPreconditionDonHoldException
import numpy as np

class State(up.model.state.ROState):
    def __init__(self, predicates: Set["up.model.fnode.Fnode"] = None):
    # def __init__(self, predicates: Set["up.model.fnode.Fnode"] = None, predecessor: Tuple["up.engine.state.State", "up.engine.action.Action"]=None):
        self.predicates = predicates if predicates else set()
        # self.predecessor = predecessor #TODO: decide if to keep or delete


    def __eq__(self, other):
        if isinstance(other, State):
            return self.predicates == other.predicates
        return False

    def get_value(self):
        return 0
    def apply(self, action: "up.engine.action.Action"):
        """
               Apply the action to this state to produce a new state.
        """

        # Make sure it is legal to run the action in the state
        if not action.pos_preconditions.issubset(self.predicates):
            msg = f"Some of the positive preconditions of action {action.name} dont hold is the current state."
            raise UPPreconditionDonHoldException(msg)

        if not action.neg_preconditions.isdisjoint(self.predicates):
            msg = f"Some of the negative preconditions of action {action.name} dont hold is the current state."
            raise UPPreconditionDonHoldException(msg)


        new_preds = set(self.predicates)
        new_preds |= set(action.add_effects)
        new_preds -= set(action.del_effects)

        add_predicates, del_predicates = self._apply_probabilistic_effects(action)
        new_preds |= add_predicates
        new_preds -= del_predicates

        # return State(new_preds, (self, action))
        return State(new_preds)

    def _apply_probabilistic_effects(self, action: "up.engine.action.Action"):
        """

        :param action: draw the outcome of the probabilistic effects
        :return: the precicates that needs to be added and removed from the state
        """
        add_predicates = set()
        del_predicates = set()

        for pe in action.probabilistic_effects:
            prob_outcomes = pe.probability_function(self)
            index = np.random.choice(len(prob_outcomes), p=list(prob_outcomes.keys()))
            values = list(prob_outcomes.values())[index]
            for v in values:
                if values[v]:
                    add_predicates.add(v)
                else:
                    del_predicates.add(v)

        return add_predicates, del_predicates
