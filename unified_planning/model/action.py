import unified_planning as up
from unified_planning.environment import get_environment, Environment
import unified_planning.shortcuts
from unified_planning.exceptions import (
    UPTypeError,
    UPUnboundedVariablesError,
    UPProblemDefinitionError,
    UPConflictingEffectsException,
    UPUsageError,
)
from fractions import Fraction
from typing import Dict, List, Set, Tuple, Union, Optional, cast, Callable
from collections import OrderedDict


# from unified_planning.model.mixins.timed_conds_effs import TimedCondsEffs


class Action:
    """This is the `Action` interface."""

    def __init__(
            self,
            _name: str,
            _parameters: Optional["OrderedDict[str, up.model.types.Type]"] = None,
            _env: Optional[Environment] = None,
            **kwargs: "up.model.types.Type",
    ):
        self._environment = get_environment(_env)
        self._name = _name
        self._parameters: "OrderedDict[str, up.model.parameter.Parameter]" = (
            OrderedDict()
        )
        if _parameters is not None:
            assert len(kwargs) == 0
            for n, t in _parameters.items():
                assert self._environment.type_manager.has_type(
                    t
                ), "type of parameter does not belong to the same environment of the action"
                self._parameters[n] = up.model.parameter.Parameter(
                    n, t, self._environment
                )
        else:
            for n, t in kwargs.items():
                assert self._environment.type_manager.has_type(
                    t
                ), "type of parameter does not belong to the same environment of the action"
                self._parameters[n] = up.model.parameter.Parameter(
                    n, t, self._environment
                )

    def __eq__(self, oth: object) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        raise NotImplementedError

    def clone(self):
        raise NotImplementedError

    @property
    def environment(self) -> Environment:
        """Returns this `Action` `Environment`."""
        return self._environment

    @property
    def name(self) -> str:
        """Returns the `Action` `name`."""
        return self._name

    @name.setter
    def name(self, new_name: str):
        """Sets the `Action` `name`."""
        self._name = new_name

    @property
    def parameters(self) -> List["up.model.parameter.Parameter"]:
        """Returns the `list` of the `Action parameters`."""
        return list(self._parameters.values())

    def parameter(self, name: str) -> "up.model.parameter.Parameter":
        """
        Returns the `parameter` of the `Action` with the given `name`.

        Example
        -------
        >>> from unified_planning.shortcuts import *
        >>> location_type = UserType("Location")
        >>> move = InstantaneousAction("move", source=location_type, target=location_type)
        >>> move.parameter("source")  # return the "source" parameter of the action, with type "Location"
        Location source
        >>> move.parameter("target")
        Location target

        If a parameter's name (1) does not conflict with an existing attribute of `Action` and (2) does not start with '_'
        it can also be accessed as if it was an attribute of the action. For instance:

        >>> move.source
        Location source

        :param name: The `name` of the target `parameter`.
        :return: The `parameter` of the `Action` with the given `name`.
        """
        if name not in self._parameters:
            raise ValueError(f"Action '{self.name}' has no parameter '{name}'")
        return self._parameters[name]

    def __getattr__(self, parameter_name: str) -> "up.model.parameter.Parameter":
        if parameter_name.startswith("_"):
            # guard access as pickling relies on attribute error to be thrown even when
            # no attributes of the object have been set.
            # In this case accessing `self._name` or `self._parameters`, would re-invoke __getattr__
            raise AttributeError(f"Action has no attribute '{parameter_name}'")
        if parameter_name not in self._parameters:
            raise AttributeError(
                f"Action '{self.name}' has no attribute or parameter '{parameter_name}'"
            )
        return self._parameters[parameter_name]


class InstantaneousAction(Action):
    """Represents an instantaneous action."""

    def __init__(
            self,
            _name: str,
            _parameters: Optional["OrderedDict[str, up.model.types.Type]"] = None,
            _env: Optional[Environment] = None,
            **kwargs: "up.model.types.Type",
    ):
        Action.__init__(self, _name, _parameters, _env, **kwargs)
        self._preconditions: List["up.model.precondition.Precondition"] = []
        self._effects: List[up.model.effect.Effect] = []
        self._probabilistic_effects: List[up.model.effect.ProbabilisticEffect] = []


    def __repr__(self) -> str:
        s = []
        s.append(f"action {self.name}")
        first = True
        for p in self.parameters:
            if first:
                s.append("(")
                first = False
            else:
                s.append(", ")
            s.append(str(p))
        if not first:
            s.append(")")
        s.append(" {\n")
        s.append("    preconditions = [\n")
        for c in self.preconditions:
            s.append(f"      {str(c)}\n")
        s.append("    ]\n")
        s.append("    effects = [\n")
        for e in self.effects:
            s.append(f"      {str(e)}\n")
        s.append("    ]\n")
        s.append("    probabilistic effects = [\n")
        for pe in self._probabilistic_effects:
            s.append(f"      {str(pe)}\n")
        s.append("    ]\n")
        s.append("  }")
        return "".join(s)

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, InstantaneousAction):
            cond = (
                    self._environment == oth._environment
                    and self._name == oth._name
                    and self._parameters == oth._parameters
            )
            return (
                    cond
                    and set(self._preconditions) == set(oth._preconditions)
                    and set(self._effects) == set(oth._effects)
                    and set(self._probabilistic_effects) == set(
                oth._probabilistic_effects)
            )
        else:
            return False

    def __hash__(self) -> int:
        res = hash(self._name)
        for ap in self._parameters.items():
            res += hash(ap)
        for p in self._preconditions:
            res += hash(p)
        for e in self._effects:
            res += hash(e)
        for pe in self._probabilistic_effects:
            res += hash(pe)
        return res

    def clone(self):
        new_params = OrderedDict(
            (param_name, param.type) for param_name, param in self._parameters.items()
        )
        new_instantaneous_action = InstantaneousAction(
            self._name, new_params, self._environment
        )
        new_instantaneous_action._preconditions = [p.clone() for p in self._preconditions]
        new_instantaneous_action._effects = [e.clone() for e in self._effects]
        new_instantaneous_action._probabilistic_effects = [pe.clone() for pe in self._probabilistic_effects]
        return new_instantaneous_action

    @property
    def preconditions(self) -> List["up.model.precondition.Precondition"]:
        """Returns the `list` of the `Action` `preconditions`."""
        return self._preconditions

    def clear_preconditions(self):
        """Removes all the `Action preconditions`"""
        self._preconditions = []

    @property
    def effects(self) -> List["up.model.effect.Effect"]:
        """Returns the `list` of the `Action effects`."""
        return self._effects

    @property
    def probabilistic_effects(self) -> List["up.model.effect.ProbabilisticEffect"]:
        """Returns the `list` of the `Action effects`."""
        return self._probabilistic_effects

    def clear_effects(self):
        """Removes all the `Action's effects`."""
        self._effects = []
        self._probabilistic_effects = []

    def add_precondition(
            self,
            precondition: Union[
                "up.model.fnode.FNode",
                "up.model.fluent.Fluent",
                "up.model.parameter.Parameter",
                bool,
            ],
            value: "up.model.expression.Expression",
    ):
        """
        Adds the given expression to `action's preconditions`.

        :param precondition: The expression that must be added to the `action's preconditions`.
        :param value: The value of the expression that must hold in the precondition

        """
        (precondition_exp, value_exp,) = self._environment.expression_manager.auto_promote(
            precondition, value
        )
        assert self._environment.type_checker.get_type(precondition_exp).is_bool_type()
        if precondition_exp == self._environment.expression_manager.TRUE():
            return
        free_vars = self._environment.free_vars_oracle.get_free_variables(
            precondition_exp
        )
        if len(free_vars) != 0:
            raise UPUnboundedVariablesError(
                f"The precondition {str(precondition_exp)} has unbounded variables:\n{str(free_vars)}"
            )
        self._add_precondition_instance(
                up.model.precondition.Precondition(precondition_exp, value_exp)
        )
    def _add_precondition_instance(self, precondition: "up.model.precondition.Precondition"):
        assert (
                precondition.environment == self._environment
        ), "precondition does not have the same environment of the action"
        if up.model.precondition.check_conflicting_precondition(
            precondition,
            self._preconditions,
            self.name
        ):
            self._preconditions.append(precondition)

    def add_effect(
            self,
            fluent: Union["up.model.fnode.FNode", "up.model.fluent.Fluent"],
            value: "up.model.expression.Expression",
    ):
        """
        Adds the given `assignment` to the `action's effects`.

        :param fluent: The `fluent` of which `value` is modified by the `assignment`.
        :param value: The `value` to assign to the given `fluent`.
        """
        (
            fluent_exp,
            value_exp,
        ) = self._environment.expression_manager.auto_promote(fluent, value)
        if not fluent_exp.is_fluent_exp():
            raise UPUsageError(
                "fluent field of add_effect must be a Fluent or a FluentExp"
            )
        if not fluent_exp.type.is_compatible(value_exp.type):
            # Value is not assignable to fluent (its type is not a subset of the fluent's type).
            raise UPTypeError(
                f"InstantaneousAction effect has an incompatible value type. Fluent type: {fluent_exp.type} // Value type: {value_exp.type}"
            )
        self._add_effect_instance(
            up.model.effect.Effect(fluent_exp, value_exp)
        )

    def _add_effect_instance(self, effect: "up.model.effect.Effect"):
        assert (
                effect.environment == self._environment
        ), "effect does not have the same environment of the action"
        up.model.effect.check_conflicting_effects(
            effect,
            None,
            "action"
        )
        self._effects.append(effect)

    def add_probabilistic_effect(
            self,
            fluents: List["up.model.fnode.FNode"],
            probability_func: Callable[
                [
                    "up.model.state.ROState",
                ],
                Dict[float, Dict["up.model.fnode.FNode", "up.model.fnode.FNode"]],
            ]
    ):
        """
        Adds the given `assignment` to the `action's probabilistic_effects`.

        :param fluents: The `fluents` of which `value` is modified by the `assignment`.
        :param probability_func: based on the probability function a value is chosen from the values param
        """

        fluents_exp = self._environment.expression_manager.auto_promote(fluents)

        for f in fluents_exp:
            if not f.is_fluent_exp():
                raise UPUsageError(
                    "fluent field of add_effect must be a Fluent or a FluentExp"
                )

        self._add_probabilistic_effect_instance(
            up.model.effect.ProbabilisticEffect(fluents_exp, probability_func)
        )

    def _add_probabilistic_effect_instance(self, probabilistic_effect: "up.model.effect.ProbabilisticEffect"):
        assert (
                probabilistic_effect.environment() == self._environment
        ), "effect does not have the same environment of the action"
        up.model.effect.check_conflicting_probabilistic_effects(
            probabilistic_effect,
            None,
            self._probabilistic_effects,
            self._effects,
            "action",
        )
        self._probabilistic_effects.append(probabilistic_effect)

    def _set_preconditions(self, preconditions: List["up.model.precondition.Precondition"]):
        self._preconditions = preconditions

    def _set_effects(self, effects: List["up.model.effect.Effect"]):
        self._effects = effects

    def _set_probabilistic_effects(self, probabilistic_effects: List["up.model.effect.ProbabilisticEffect"]):
        self._probabilistic_effects = probabilistic_effects


class DurativeAction(Action):
    """Represents a durative action."""

    def __init__(  # TODO: should I add fluents assignment like in instantaneous action
            self,
            _name: str,
            _parameters: Optional["OrderedDict[str, up.model.types.Type]"] = None,
            _env: Optional[Environment] = None,
            **kwargs: "up.model.types.Type",
    ):
        Action.__init__(self, _name, _parameters, _env, **kwargs)
        self._duration: "up.model.timing.DurationInterval" = (
            up.model.timing.FixedDuration(self._environment.expression_manager.Int(0))
        )
        self._preconditions: Dict[str, List["up.model.precondition.Precondition"]] = {}
        self._start_effects: List[up.model.effect.Effect] = []
        self._effects: List[up.model.effect.Effect] = []
        self._probabilistic_effects: List[up.model.effect.ProbabilisticEffect] = []


    def __repr__(self) -> str:
        s = []
        s.append(f"durative action {self.name}")
        first = True
        for p in self.parameters:
            if first:
                s.append("(")
                first = False
            else:
                s.append(", ")
            s.append(str(p))
        if not first:
            s.append(")")
        s.append(" {\n")
        s.append("    preconditions = [\n")
        for t in self.preconditions:
            s.append(f"      {str(t)}\n")
            for p in self.preconditions[t]:
                s.append(f"      {str(p)}\n")
        s.append("    ]\n")
        s.append(f"    duration = {str(self._duration)}\n")
        s.append("   start effects = [\n")
        for de in self.start_effects:
            s.append(f"      {str(de)}\n")
        s.append("    ]\n")
        s.append("    effects = [\n")
        for e in self.effects:
            s.append(f"      {str(e)}\n")
        s.append("    ]\n")
        s.append("    probabilistic effects = [\n")
        for pe in self._probabilistic_effects:
            s.append(f"      {str(pe)}\n")
        s.append("    ]\n")
        s.append("  }")
        return "".join(s)

    def __eq__(self, oth: object) -> bool:
        if not isinstance(oth, DurativeAction):
            return False
        if (
                self._environment != oth._environment
                or self._name != oth._name
                or self._parameters != oth._parameters
                or self._duration != oth._duration
                or set(self._preconditions) != set(oth._preconditions)
                or set(self._effects) != set(oth._effects)
                or set(self._probabilistic_effects) != set(
            oth._probabilistic_effects)
                or set(self.start_effects) != set(oth._start_effects)
        ):
            return False
        return True

    def __hash__(self) -> int:
        res = hash(self._name) + hash(self._duration)
        for ap in self._parameters.items():
            res += hash(ap)
        for p in self._preconditions:
            res += hash(p)
        for e in self._effects:
            res += hash(e)
        for pe in self._probabilistic_effects:
            res += hash(pe)
        for de in self._start_effects:
            res += hash(de)
        return res

    def clone(self):
        new_params = OrderedDict(
            (param_name, param.type) for param_name, param in self._parameters.items()
        )
        new_durative_action = DurativeAction(self._name, new_params, self._environment)
        new_durative_action._duration = self._duration
        new_durative_action._preconditions = {p_type: [p.clone() for p in preconditions] for p_type, preconditions in self._preconditions.items()}
        new_durative_action._effects = [e.clone() for e in self._effects]
        new_durative_action._probabilistic_effects = [pe.clone() for pe in self._probabilistic_effects]
        new_durative_action._start_effects = [de.clone() for de in self._start_effects]

        return new_durative_action

    @property
    def preconditions(self) -> Dict[str, List["up.model.precondition.Precondition"]]:
        """Returns the `list` of the `Action` `preconditions`."""
        return self._preconditions

    def clear_preconditions(self):
        """Removes all the `Action preconditions`"""
        self._preconditions = []

    @property
    def effects(self) -> List["up.model.effect.Effect"]:
        """Returns the `list` of the `Action effects`."""
        return self._effects

    @property
    def start_effects(self) -> List["up.model.effect.Effect"]:
        """Returns the `list` of the `Action effects`."""
        return self._start_effects

    @property
    def probabilistic_effects(self) -> List["up.model.effect.ProbabilisticEffect"]:
        """Returns the `list` of the `Action effects`."""
        return self._probabilistic_effects

    def clear_effects(self):
        """Removes all the `Action's effects`."""
        self._effects = []
        self._probabilistic_effects = []
        self._start_effects = []

    @property
    def duration(self) -> "up.model.timing.DurationInterval":
        """Returns the `action` `duration interval`."""
        return self._duration

    def set_fixed_duration(self, value: Union["up.model.fnode.FNode", int, Fraction]):
        """
        Sets the `duration interval` for this `action` as the interval `[value, value]`.

        :param value: The `value` set as both edges of this `action's duration`.
        """
        (value_exp,) = self._environment.expression_manager.auto_promote(value)
        duration = up.model.timing.FixedDuration(value_exp)
        value = duration.lower
        tvalue = self._environment.type_checker.get_type(value)
        assert tvalue.is_int_type() or tvalue.is_real_type()
        self._duration = up.model.timing.FixedDuration(value_exp)

    def add_precondition(
            self,
            preconditionTiming: "up.model.timing.PreconditionTimepoint",
            precondition: Union[
                "up.model.fnode.FNode",
                "up.model.fluent.Fluent",
                "up.model.parameter.Parameter",
                bool,
            ],
            value: "up.model.expression.Expression",
    ):
        """
        Adds the given expression to `action's preconditions`.

        :param preconditionTiming: The timing the precondition must hold.
        :param precondition: The expression that must be added to the `action's preconditions`.
        :param value: The value of the expression that must hold in the precondition
        """
        (precondition_exp, value_exp,) = self._environment.expression_manager.auto_promote(
            precondition, value
        )
        assert self._environment.type_checker.get_type(precondition_exp).is_bool_type()
        if precondition_exp == self._environment.expression_manager.TRUE():
            return
        free_vars = self._environment.free_vars_oracle.get_free_variables(
            precondition_exp
        )
        if len(free_vars) != 0:
            raise UPUnboundedVariablesError(
                f"The precondition {str(precondition_exp)} has unbounded variables:\n{str(free_vars)}"
            )
        name = preconditionTiming.kind.name
        self._add_precondition_instance(name, up.model.Precondition(precondition_exp, value_exp))
    def _add_precondition_instance(self,  preconditionTimingName: str, precondition: "up.model.precondition.Precondition"):
        assert (
                precondition.environment == self._environment
        ), "precondition does not have the same environment of the action"
        if up.model.precondition.check_conflicting_durative_precondition(
                preconditionTimingName,
                precondition,
                self._preconditions,
                self.name
        ):

            if preconditionTimingName in self._preconditions:
                self._preconditions[preconditionTimingName].append(precondition)
            else:
                self._preconditions[preconditionTimingName] = [precondition]


    def add_effect(
            self,
            fluent: Union["up.model.fnode.FNode", "up.model.fluent.Fluent"],
            value: "up.model.expression.Expression",
    ):
        """
        Adds the given `assignment` to the `action's effects`.

        :param fluent: The `fluent` of which `value` is modified by the `assignment`.
        :param value: The `value` to assign to the given `fluent`..
        """
        (
            fluent_exp,
            value_exp,
        ) = self._environment.expression_manager.auto_promote(fluent, value)
        if not fluent_exp.is_fluent_exp():
            raise UPUsageError(
                "fluent field of add_effect must be a Fluent or a FluentExp"
            )
        if not fluent_exp.type.is_compatible(value_exp.type):
            # Value is not assignable to fluent (its type is not a subset of the fluent's type).
            raise UPTypeError(
                f"InstantaneousAction effect has an incompatible value type. Fluent type: {fluent_exp.type} // Value type: {value_exp.type}"
            )
        self._add_effect_instance(
            up.model.effect.Effect(fluent_exp, value_exp)
        )

    def _add_effect_instance(self, effect: "up.model.effect.Effect"):
        assert (
                effect.environment == self._environment
        ), "effect does not have the same environment of the action"
        up.model.effect.check_conflicting_effects(
            effect,
            None,
            "action"
        )
        self._effects.append(effect)

    def add_start_effect(
            self,
            fluent: Union["up.model.fnode.FNode", "up.model.fluent.Fluent"],
            value: "up.model.expression.Expression",
    ):
        """
        Adds the given `assignment` to the `action's effects`.

        :param fluent: The `fluent` of which `value` is modified by the `assignment`.
        :param value: The `value` to assign to the given `fluent`.
        """
        (
            fluent_exp,
            value_exp,
        ) = self._environment.expression_manager.auto_promote(fluent, value)
        if not fluent_exp.is_fluent_exp():
            raise UPUsageError(
                "fluent field of add_effect must be a Fluent or a FluentExp"
            )
        if not fluent_exp.type.is_compatible(value_exp.type):
            # Value is not assignable to fluent (its type is not a subset of the fluent's type).
            raise UPTypeError(
                f"InstantaneousAction effect has an incompatible value type. Fluent type: {fluent_exp.type} // Value type: {value_exp.type}"
            )
        self._add_start_effect_instance(
            up.model.effect.Effect(fluent_exp, value_exp)
        )

    def _add_start_effect_instance(self, effect: "up.model.effect.Effect"):
        assert (
                effect.environment == self._environment
        ), "effect does not have the same environment of the action"
        up.model.effect.check_conflicting_effects(
            effect,
            None,
            "action"
        )
        self._start_effects.append(effect)

    def add_probabilistic_effect(
            self,
            fluents: List["up.model.fnode.FNode"],
            probability_func: Callable[
                [
                    "up.model.state.ROState",
                ],
                Dict[float, Dict["up.model.fnode.FNode", "up.model.fnode.FNode"]],
            ]
    ):
        """
        Adds the given `assignment` to the `action's probabilistic_effects`.

        :param fluents: The `fluents` of which `value` is modified by the `assignment`.
        :param probability_func: based on the probability function a value is chosen from the values param
        """

        fluents_exp = self._environment.expression_manager.auto_promote(fluents)

        for f in fluents_exp:
            if not f.is_fluent_exp():
                raise UPUsageError(
                    "fluent field of add_effect must be a Fluent or a FluentExp"
                )

        self._add_probabilistic_effect_instance(
            up.model.effect.ProbabilisticEffect(fluents_exp, probability_func)
        )

    def _add_probabilistic_effect_instance(self, probabilistic_effect: "up.model.effect.ProbabilisticEffect"):
        assert (
                probabilistic_effect.environment() == self._environment
        ), "effect does not have the same environment of the action"
        up.model.effect.check_conflicting_probabilistic_effects(
            probabilistic_effect,
            None,
            self._probabilistic_effects,
            self._effects,
            "action",
        )
        self._probabilistic_effects.append(probabilistic_effect)

    def _set_preconditions(self, preconditions: Dict["up.model.timing.PreconditionTimepoint", List["up.model.precondition.Precondition"]]):
        self._preconditions = preconditions


class InstantaneousStartAction(InstantaneousAction):
    """Represents a start action with fix duration.
    This is the start action of the DurativeAction action class
    _end_action - the end action of this start action """
    def __init__(
            self,
            _name: str,
            _parameters: Optional["OrderedDict[str, up.model.types.Type]"] = None,
            _env: Optional[Environment] = None,
            **kwargs: "up.model.types.Type",
    ):
        InstantaneousAction.__init__(self, _name, _parameters, _env, **kwargs)
        self._duration: "up.model.timing.DurationInterval" = (
            up.model.timing.FixedDuration(self._environment.expression_manager.Int(0)))
        self._end_action: InstantaneousAction = None
    def __repr__(self) -> str:
        b = InstantaneousAction.__repr__(self)[0:-3]
        s = ["Instantaneous start ", b]
        s.append(f"    duration = {str(self._duration)}\n")
        s.append(f" end action = {self._end_action.name}")
        s.append("  }")
        return "".join(s)

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, InstantaneousStartAction):
            super().__eq__(oth) and \
            self._duration == oth._duration and \
                self._end_action == oth._end_action
        else:
            return False

    def __hash__(self) -> int:
        return super().__hash__() + hash(self._duration) + self._end_action.__hash__()

    def clone(self):
        new_params = OrderedDict()
        for param_name, param in self._parameters.items():
            new_params[param_name] = param.type
        new_instantaneous_start_action = InstantaneousStartAction(self._name, new_params, self._environment)
        new_instantaneous_start_action._duration = self._duration
        new_instantaneous_start_action._end_action = self._end_action.clone()

        return new_instantaneous_start_action

    def duration(self) -> "up.model.timing.DurationInterval":
        """Returns the `action` `duration interval`."""
        return self._duration
    def _set_fixed_duration(self, duration: "up.model.timing.DurationInterval"):
        """
        Sets the `duration interval` for this `action` as the interval `[value, value]`.

        :param duration: The `duration` of this `action's`.
        """
        self._duration = duration

    def _set_end_action(self, end_action: InstantaneousAction):
        """Sets the `end_action`."""
        self._end_action = end_action

    def end_action(self) -> InstantaneousAction:
        """Returns the `end_action`ץ"""
        return self._end_action


