"""
This module defines the `Precondition` class.
A basic `Precondition` has a `fluent` and an `expression`.
"""


import unified_planning as up
from unified_planning.exceptions import UPConflictingEffectsException
from enum import Enum, auto
from typing import List, Callable, Dict, Optional, Set, Tuple, Union
import numpy as np
import inspect as i

class Precondition:
    """
    This class represent an precondition. It has a :class:`~unified_planning.model.Fluent`,  and a value
    that determines what is the `Fluent` value needed for the execution of the action.
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
        if isinstance(oth, Precondition):
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
        new_precondition = Precondition(self._fluent, self._value)
        return new_precondition

    @property
    def fluent(self) -> "up.model.fnode.FNode":
        """Returns the `Fluent` of this `precondition`."""
        return self._fluent

    @property
    def value(self) -> "up.model.fnode.FNode":
        """Returns the `value` of the `Fluent` needed for the action execution."""
        return self._value

    def set_value(self, new_value: "up.model.fnode.FNode"):
        """
        Sets the `value` needed to the `Precondition` of the `Fluent`.

        :param new_value: The `value` that will determine this `precondition's value`.
        """
        self._value = new_value


    @property
    def environment(self) -> "up.environment.Environment":
        """Returns this `Precondition's Environment`."""
        return self._fluent.environment
