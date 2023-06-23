"""
This module defines the `Precondition` class.
A basic `Precondition` has a `fluent` and an `expression`.
"""


import unified_planning as up
from unified_planning.exceptions import UPConflictingPreconditionException
from typing import List, Dict


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


def check_conflicting_precondition(precondition: "up.model.Precondition", action_preconditions: List["up.model.Precondition"], name: str):
    """
    This method checks if the precondition that would be added is in conflict with the preconditions
    already in the action.

    :param precondition: The target precondition to add.
    :param action_preconditions: The preconditions already defined in the action
    :param name: string used for better error indexing.

     :raises: UPConflictingException if the given precondition is in conflict with the preconditions already in the action.
     :returns: `False` if the precondition is already in the preconditions of the action, otherwise returns `True`
    """

    for p in action_preconditions:
        if precondition == p:
            return False
        if precondition._fluent == p._fluent:
            msg = f"The precondition {precondition} is in conflict with a precondition already in the {name}."
            raise UPConflictingPreconditionException(msg)
    return True


def check_conflicting_durative_precondition(preconditionTiming: str, precondition: "up.model.Precondition", action_preconditions: Dict["up.model.timing.PreconditionTimepoint", List["up.model.Precondition"]], name: str):
    """
    This method checks if the precondition that would be added is in conflict with the preconditions
    already in the action.

    :param preconditionTiming: The target precondition timing - START, OVERALL, END
    :param precondition: The target precondition to add.
    :param action_preconditions: The preconditions already defined in the action
    :param name: string used for better error indexing.

     :raises: UPConflictingException if the given precondition is in conflict with the preconditions already in the action.
     :returns: `False` if the precondition is already in the preconditions of the action, otherwise returns `True`
    """

    for p_type in action_preconditions:
        if p_type in ['START', 'OVERALL'] and preconditionTiming in ['START', 'OVERALL']:

            if any(precondition == p for p in action_preconditions[p_type]):
                if p_type == preconditionTiming:
                    return False
                else:
                    msg = f"The precondition {precondition} is in conflict with a precondition already in the {name}."
                    raise UPConflictingPreconditionException(msg)

            if any(precondition._fluent == p._fluent for p in action_preconditions[p_type]):
                msg = f"The precondition {precondition} is in conflict with a precondition already in the {name}."
                raise UPConflictingPreconditionException(msg)

        if p_type in ['END', 'OVERALL'] and preconditionTiming in ['END', 'OVERALL']:

            if any(precondition == p for p in action_preconditions[p_type]):
                if p_type == preconditionTiming:
                    return False
                else:
                    msg = f"The precondition {precondition} is in conflict with a precondition already in the {name}."
                    raise UPConflictingPreconditionException(msg)

            if any(precondition._fluent == p._fluent for p in action_preconditions[p_type]):
                msg = f"The precondition {precondition} is in conflict with a precondition already in the {name}."
                raise UPConflictingPreconditionException(msg)
    return True