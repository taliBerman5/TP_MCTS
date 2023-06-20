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
    that determines how the `Fluent` is modified, a `condition` that determines if the `Effect`
    is actually applied or not and an `EffectKind` that determines the semantic of the `Effect`.
    """

    def __init__(
        self,
        fluent: "up.model.fnode.FNode",
        value: "up.model.fnode.FNode",
        condition: "up.model.fnode.FNode",
    ):
        self._fluent = fluent
        self._value = value
        self._condition = condition
        assert (
            fluent.environment == value.environment
            and value.environment == condition.environment
        ), "Effect expressions have different environment."

    def __repr__(self) -> str:
        s = []
        if self.is_conditional():
            s.append(f"if {str(self._condition)} then")
        s.append(f"{str(self._fluent)}")
        s.append(f"{str(self._value)}")
        return " ".join(s)

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, Effect):
            return (
                self._fluent == oth._fluent
                and self._value == oth._value
                and self._condition == oth._condition
            )
        else:
            return False

    def __hash__(self) -> int:
        return (
            hash(self._fluent)
            + hash(self._value)
            + hash(self._condition)
            + hash(self._kind)
        )

    def clone(self):
        new_effect = Effect(self._fluent, self._value, self._condition, self._kind)
        return new_effect

    def is_conditional(self) -> bool:
        """
        Returns `True` if the `Effect` condition is not `True`; this means that the `Effect` might
        not always be applied but depends on the runtime evaluation of it's :func:`condition <unified_planning.model.Effect.condition>`.
        """
        return not self._condition.is_true()

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
    def condition(self) -> "up.model.fnode.FNode":
        """Returns the `condition` required for this `Effect` to be applied."""
        return self._condition

    def set_condition(self, new_condition: "up.model.fnode.FNode"):
        """
        Sets the `condition` required for this `Effect` to be applied.

        :param new_condition: The expression set as this `effect's condition`.
        """
        self._condition = new_condition

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


def check_conflicting_effects(
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

    raise NotImplementedError
