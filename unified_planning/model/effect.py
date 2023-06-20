"""
This module defines the `Effect` class.
A basic `Effect` has a `fluent` and an `expression`.
A `condition` can be added to make it a `conditional effect`.
"""


import unified_planning as up
from unified_planning.exceptions import UPConflictingEffectsException
from enum import Enum, auto
from typing import List, Callable, Dict, Optional, Set, Tuple, Union
import numpy as np
import inspect as i

class Effect:
    """
    This class represent an effect. It has a :class:`~unified_planning.model.Fluent`, modified by this effect, a value
    that determines how the `Fluent` is modified.
    """

    def __init__(
        self,
        fluent: "up.model.fnode.FNode",
        value: "up.model.fnode.FNode",
    ):
        self._fluent = fluent
        self._value = value
        assert (
            fluent.environment == value.environment
        ), "Effect expressions have different environment."

    def __repr__(self) -> str:
        s = []
        s.append(f"{str(self._fluent)}")
        s.append(f"{str(self._value)}")
        return " ".join(s)

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, Effect):
            return (
                self._fluent == oth._fluent
                and self._value == oth._value
            )
        else:
            return False

    def __hash__(self) -> int:
        return (
            hash(self._fluent)
            + hash(self._value)
        )

    def clone(self):
        new_effect = Effect(self._fluent, self._value)
        return new_effect

    @property
    def fluent(self) -> "up.model.fnode.FNode":
        """Returns the `Fluent` that is modified by this `Effect`."""
        return self._fluent

    @property
    def value(self) -> "up.model.fnode.FNode":
        """Returns the `value` given to the `Fluent` by this `Effect`."""
        return self._value

    def set_value(self, new_value: "up.model.fnode.FNode"):
        """
        Sets the `value` given to the `Fluent` by this `Effect`.

        :param new_value: The `value` that will be set as this `effect's value`.
        """
        self._value = new_value


    @property
    def environment(self) -> "up.environment.Environment":
        """Returns this `Effect's Environment`."""
        return self._fluent.environment


class ProbabilisticEffect:
    """
    This class represents a `probabilistic effect` over a list of :class:`~unified_planning.model.Fluent` expressions.
    The `fluent's parameters` must be constants or :class:`~unified_planning.model.Action` `parameters`.
    The callable probability_func must return the result of the `probabilistic effects` applied
    in the given :class:`~unified_planning.model.State` for the specified `fluent` expressions.
    """

    def __init__(
        self,
        fluents: List["up.model.fnode.FNode"],
        probability_func: Callable[
            [
                "up.model.problem.AbstractProblem",
                "up.model.state.ROState",
            ],
            Dict[float, Dict["up.model.fnode.FNode", "up.model.fnode.FNode"]],
        ]
    ):
        for f in fluents:
            if not f.is_fluent_exp():
                raise up.exceptions.UPUsageError(
                    "probabilistic effects can be defined on fluent expressions"
                )

        self._fluents = fluents
        self._probability_func = probability_func


    def __repr__(self) -> str:  #TODO: TB maybe needs to be changed
        s = []
        s.append(f"{self._fluents}:= probabilistic")
        func = i.getsource(self._probability_func)
        return_statement = func[func.index("return ") + len("return "):]
        s.append(return_statement)
        return " ".join(s)

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, ProbabilisticEffect):
            return self._fluents == oth._fluents and self._probability_func == oth._probability_func
        else:
            return False

    def __hash__(self) -> int:
        res = hash(self._probability_func)
        for f in self._fluents:
            res += hash(f)
        return res

    def environment(self) -> "up.environment.Environment":
        """Returns this `Effect's Environment`."""
        return self._fluents[0].environment

    def clone(self):
        new_probabilistic_effect = ProbabilisticEffect(self._fluents, self._probability_func)
        return new_probabilistic_effect

    @property
    def fluents(self) -> List["up.model.fnode.FNode"]:
        """Returns the `Fluents` that is modified by this `Effect`."""
        return self._fluents

    @property
    def probability_function(
        self,
    ) -> Callable[
        [
            "up.model.problem.AbstractProblem",
            "up.model.state.ROState",
        ],
        List["up.model.fnode.FNode"],
    ]:
        """
        Return the function that contains the information on how the `fluent` of this `ProbabilisticEffect`
        is modified when this `probabilistic effect` is applied.
        """
        return self._probability_func


def check_conflicting_effects( #TODO: need to update
    effect: Effect,
    timing: Optional["unified_planning.model.timing.Timing"],
    fluents: Dict["unified_planning.model.fnode.FNode", "unified_planning.model.fnode.FNode"],
    name: str,
):
    """
    This method checks if the effect that would be added is in conflict with the effects/simulated-effects
    already in the action/problem.

    Note: This method has side effects on the fluents_assigned mapping and the fluents_inc_dec set, based
        on the given effect.

    :param effect: The target effect to add.
    :param timing: Optionally, the timing at which the effect is performed; None if the timing
        is not meaningful, like in InstantaneousActions.
    :param fluents: The mapping from a fluent to it's value of the effects happening in the
        same instant of the given effect.
    :param name: string used for better error indexing.
    :raises: UPConflictingException if the given effect is in conflict with the data structure around it.
    """

    #raise NotImplementedError
    return

def check_conflicting_probabilistic_effects(  #TODO: need to update
    probabilistic_effect: ProbabilisticEffect,
    timing: Optional["up.model.timing.Timing"],
    fluents_assigned: Dict["up.model.fnode.FNode", "up.model.fnode.FNode"],
    probabilistic_effects: List[ProbabilisticEffect],
    effects: List[Effect],

    name: str,
):
    """
    This method checks if the simulated effect that would be added is in conflict with the effects
    already in the action/problem.

    :param probabilistic_effect: The target simulated_effect to add.
    :param timing: Optionally, the timing at which the simulated_effect is performed; None if the timing
        is not meaningful, like in InstantaneousActions.
    :param fluents_assigned: The mapping from a fluent to it's value of the effects happening in the
        same instant of the given simulated_effect.
    :param probabilistic_effects: The list of probabilistic effects that happens in the same moment of the effect.
    :param effects: The list of effects that happens in the same moment of the effect.
    :param name: string used for better error indexing.
    :raises: UPConflictingException if the given simulated_effect is in conflict with the data structure around it.
    """
    for f in probabilistic_effect.fluents:
        if f in fluents_assigned:
            if timing is None:
                msg = f"The probabilistic effect {probabilistic_effect} is in conflict with the effects already in the {name}."
            else:
                msg = f"The probabilistic effect {probabilistic_effect} at timing {timing} is in conflict with the effects already in the {name}."
            raise UPConflictingEffectsException(msg)


        elif (
                effects
        ):
            effects_fluents = [effect.fluent for effect in effects]
            if f in effects_fluents:
                if timing is None:
                    msg = f"The effect {probabilistic_effect} is in conflict with the effects already in the {name}."
                else:
                    msg = f"The effect {probabilistic_effect} at timing {timing} is in conflict with the effects already in the {name}."
                raise UPConflictingEffectsException(msg)

        elif (
                probabilistic_effects
        ):
            probabilistic__effects_fluents = list(np.concatenate([effect.fluents for effect in probabilistic_effects]).flat)
            if f in probabilistic__effects_fluents:
                if timing is None:
                    msg = f"The effect {probabilistic_effect} is in conflict with the probabilistic_ effects already in the {name}."
                else:
                    msg = f"The effect {probabilistic_effect} at timing {timing} is in conflict with the probabilistic_ effects already in the {name}."
                raise UPConflictingEffectsException(msg)