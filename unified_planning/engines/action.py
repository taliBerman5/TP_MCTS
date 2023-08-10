import unified_planning as up
from unified_planning.environment import get_environment, Environment
import unified_planning.shortcuts
from unified_planning.exceptions import (
    UPTypeError,
    UPUnboundedVariablesError,
    UPProblemDefinitionError,
    UPConflictingEffectsException,
    UPUsageError,
    UPConflictingPreconditionException,
)
from fractions import Fraction
from typing import Dict, List, Set, Tuple, Union, Optional, cast, Callable
from collections import OrderedDict

""" The engine action interface splits positive and negative preconditions and effect for convenient"""


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
        self._neg_preconditions: Set["up.model.fnode.FNode"] = set()
        self._pos_preconditions: Set["up.model.fnode.FNode"] = set()
        self._del_effects: Set["up.model.fnode.FNode"] = set()
        self._add_effects: Set["up.model.fnode.FNode"] = set()
        self._probabilistic_effects: List[up.model.effect.ProbabilisticEffect] = []
        # fluent assigned is the mapping of the fluent to it's value
        self._fluents_assigned: Dict[
            "up.model.fnode.FNode", "up.model.fnode.FNode"
        ] = {}

    @classmethod
    def init_from_action(cls, action: "up.model.InstantaneousAction"):
        engine_action = up.engines.InstantaneousAction(action._name)
        engine_action._parameters = action._parameters
        engine_action._set_preconditions(action.preconditions)
        engine_action._set_effects(action.effects)
        engine_action._set_probabilistic_effects(action.probabilistic_effects)
        return engine_action

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
        s.append("  negative preconditions = [\n")
        for c in self.neg_preconditions:
            s.append(f"      {str(c)}\n")
        s.append("    ]\n")
        s.append("  positive preconditions = [\n")
        for c in self.pos_preconditions:
            s.append(f"      {str(c)}\n")
        s.append("    ]\n")
        s.append("  delete effects = [\n")
        for e in self.del_effects:
            s.append(f"      {str(e)}\n")
        s.append("    ]\n")
        s.append("  add effects = [\n")
        for e in self.add_effects:
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
                    and set(self._neg_preconditions) == set(oth._neg_preconditions)
                    and set(self._pos_preconditions) == set(oth._pos_preconditions)
                    and set(self._del_effects) == set(oth._del_effects)
                    and set(self._add_effects) == set(oth._add_effects)
                    and set(self._probabilistic_effects) == set(
                oth._probabilistic_effects)
            )
        else:
            return False

    def __hash__(self) -> int:
        res = hash(self._name)
        for ap in self._parameters.items():
            res += hash(ap)
        for p in self._neg_preconditions:
            res += hash(p)
        for p in self._pos_preconditions:
            res += hash(p)
        for e in self._del_effects:
            res += hash(e)
        for e in self._add_effects:
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
        new_instantaneous_action._neg_preconditions = set(self._neg_preconditions)
        new_instantaneous_action._pos_preconditions = set(self._pos_preconditions)
        new_instantaneous_action._del_effects = set(self._del_effects)
        new_instantaneous_action._add_effects = set(self._add_effects)
        new_instantaneous_action._probabilistic_effects = [pe.clone() for pe in self._probabilistic_effects]
        new_instantaneous_action._fluents_assigned = self._fluents_assigned.copy()
        return new_instantaneous_action

    @property
    def neg_preconditions(self) -> Set["up.model.fnode.Fnode"]:
        """Returns the `list` of the `Action` negative `preconditions`."""
        return self._neg_preconditions

    @property
    def pos_preconditions(self) -> Set["up.model.fnode.Fnode"]:
        """Returns the `list` of the `Action` positive `preconditions`."""
        return self._pos_preconditions

    @property
    def del_effects(self) -> Set["up.model.fnode.Fnode"]:
        """Returns the `list` of the delete `Action effects`."""
        return self._del_effects

    @property
    def add_effects(self) -> Set["up.model.fnode.Fnode"]:
        """Returns the `list` of the `Action effects`."""
        return self._add_effects

    @property
    def probabilistic_effects(self) -> List["up.model.effect.ProbabilisticEffect"]:
        """Returns the `list` of the `Action effects`."""
        return self._probabilistic_effects

    def _set_preconditions(self, preconditions: List["up.model.precondition.Precondition"]):
        self._neg_preconditions = set([p.fluent for p in preconditions if not p.value.constant_value()])
        self._pos_preconditions = set([p.fluent for p in preconditions if p.value.constant_value()])

    def _set_effects(self, effects: List["up.model.effect.Effect"]):
        self._del_effects = set([e.fluent for e in effects if not e.value.constant_value()])
        self._add_effects = set([e.fluent for e in effects if e.value.constant_value()])

    def _set_probabilistic_effects(self, probabilistic_effects: List["up.model.effect.ProbabilisticEffect"]):
        self._probabilistic_effects = probabilistic_effects

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
        if value_exp.constant_value():
            if precondition_exp in self._neg_preconditions:
                msg = f"The precondition {precondition} is in conflict with a precondition already in the {self.name}."
                raise UPConflictingPreconditionException(msg)
            self._pos_preconditions.add(precondition_exp)
        else:
            if precondition_exp in self._pos_preconditions:
                msg = f"The precondition {precondition} is in conflict with a precondition already in the {self.name}."
                raise UPConflictingPreconditionException(msg)
            self._neg_preconditions.add(precondition_exp)

    def add_preconditions(self, preconditions: List["up.model.precondition.Precondition"]):
        for p in preconditions:
            self.add_precondition(p.fluent, p.value)

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

        if value_exp.constant_value():
            if fluent_exp in self._del_effects:
                msg = f"The effect {fluent_exp} is in conflict with an effect already in the {self.name}."
                raise UPConflictingEffectsException(msg)
            self._add_effects.add(fluent_exp)
        else:
            if fluent_exp in self._add_effects:
                msg = f"The effect {fluent_exp} is in conflict with an effect already in the {self.name}."
                raise UPConflictingEffectsException(msg)
            self._del_effects.add(fluent_exp)


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
        self._end_action: Optional[InstantaneousEndAction] = None

    def __repr__(self) -> str:
        b = InstantaneousAction.__repr__(self)[0:-3]
        s = ["Instantaneous start ", b]
        s.append(f"    duration = {str(self._duration)}\n")
        s.append(f" end action = {self._end_action.name}")
        s.append("  }")
        return "".join(s)

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, InstantaneousStartAction):
            return super().__eq__(oth) and \
                self._duration == oth._duration
        else:
            return False

    def __hash__(self) -> int:
        return super().__hash__() + hash(self._duration)

    def clone(self):
        new_params = OrderedDict()
        for param_name, param in self._parameters.items():
            new_params[param_name] = param.type
        new_instantaneous_start_action = InstantaneousStartAction(self._name, new_params, self._environment)
        new_instantaneous_start_action._duration = self._duration
        new_instantaneous_start_action._end_action = self._end_action.clone()

        return new_instantaneous_start_action

    @property
    def duration(self) -> "up.model.timing.DurationInterval":
        """Returns the `action` `duration interval`."""
        return self._duration

    def _set_fixed_duration(self, duration: "up.model.timing.DurationInterval"):
        """
        Sets the `duration interval` for this `action` as the interval `[value, value]`.

        :param duration: The `duration` of this `action's`.
        """
        self._duration = duration

    def _set_end_action(self, end_action: "up.engines.action.InstantaneousEndAction"):
        """Sets the `end_action`."""
        self._end_action = end_action

    @property
    def end_action(self) -> "up.engines.action.InstantaneousEndAction":
        """Returns the `end_action`"""
        return self._end_action


class InstantaneousEndAction(InstantaneousAction):
    """Represents a end action with fix duration.
    This is the end action of the DurativeAction action class
    _start_action - the start action of this end action """

    def __init__(
            self,
            _name: str,
            _parameters: Optional["OrderedDict[str, up.model.types.Type]"] = None,
            _env: Optional[Environment] = None,
            **kwargs: "up.model.types.Type",
    ):
        InstantaneousAction.__init__(self, _name, _parameters, _env, **kwargs)
        self._start_action: Optional[InstantaneousStartAction] = None

    def __repr__(self) -> str:
        b = InstantaneousAction.__repr__(self)[0:-3]
        s = ["Instantaneous end ", b]
        s.append(f" start action = {self._start_action.name}")
        s.append("  }")
        return "".join(s)

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, InstantaneousEndAction):
            return super().__eq__(oth)
        else:
            return False

    def __hash__(self) -> int:
        return super().__hash__()

    def clone(self):
        new_params = OrderedDict()
        for param_name, param in self._parameters.items():
            new_params[param_name] = param.type
        new_instantaneous_end_action = InstantaneousEndAction(self._name, new_params, self._environment)
        new_instantaneous_end_action._start_action = self._start_action.clone()

        return new_instantaneous_end_action

    def _set_start_action(self, start_action: InstantaneousStartAction):
        """Sets the `end_action`."""
        self._start_action = start_action

    @property
    def start_action(self) -> InstantaneousStartAction:
        """Returns the `end_action`ץ"""
        return self._start_action


class DurativeAction(InstantaneousAction):
    """Represents a durative action with fix duration.
    This durative action has no intermediate effects and
    the preconditions (no matter if start/overall/end) are treated the same
   """

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
        self._inExecution: Set["up.model.fnode.FNode"] = set()

    @classmethod
    def init_from_action(cls, action: "up.model.DurativeAction"):
        engine_action = up.engines.DurativeAction(action._name)
        engine_action._parameters = action._parameters
        engine_action._set_preconditions(action.preconditions)
        engine_action._set_effects(action.effects)
        engine_action._set_probabilistic_effects(action.probabilistic_effects)
        engine_action._set_fixed_duration(action.duration)
        return engine_action

    def __repr__(self) -> str:
        b = InstantaneousAction.__repr__(self)[0:-3]
        s = ["Duration ", b]
        s.append(f"    duration = {str(self._duration)}\n")
        s.append("  }")
        return "".join(s)

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, DurativeAction):
            return super().__eq__(oth) and \
                self._duration == oth._duration
        else:
            return False

    def __hash__(self) -> int:
        return super().__hash__() + hash(self._duration)

    def clone(self):
        new_params = OrderedDict()
        for param_name, param in self._parameters.items():
            new_params[param_name] = param.type
        new_durative_action = DurativeAction(self._name, new_params, self._environment)
        new_durative_action._duration = self._duration

        return new_durative_action

    @property
    def inExecution(self):
        return self._inExecution

    def _set_preconditions(self, preconditions: Dict[
        "up.model.timing.PreconditionTimepoint", List["up.model.precondition.Precondition"]]):
        for p_type in preconditions:
            self._neg_preconditions.update(
                set([p.fluent for p in preconditions[p_type] if not p.value.constant_value()]))
            self._pos_preconditions.update(set([p.fluent for p in preconditions[p_type] if p.value.constant_value()]))

    @property
    def duration(self) -> "up.model.timing.DurationInterval":
        """Returns the `action` `duration interval`."""
        return self._duration

    def _set_fixed_duration(self, duration: "up.model.timing.DurationInterval"):
        """
        Sets the `duration interval` for this `action` as the interval `[value, value]`.

        :param duration: The `duration` of this `action's`.
        """
        self._duration = duration

    def set_inExecution(self, inExecution: Set["up.model.fnode.FNode"]):
        self._inExecution = inExecution.copy()


class CombinationAction(Action):
    def __init__(
            self,
            _name: str,
            _parameters: Optional["OrderedDict[str, up.model.types.Type]"] = None,
            _env: Optional[Environment] = None,
            **kwargs: "up.model.types.Type",
    ):
        Action.__init__(self, _name, _parameters, _env, **kwargs)
        self._neg_preconditions: Set["up.model.fnode.FNode"] = set()
        self._pos_preconditions: Set["up.model.fnode.FNode"] = set()
        self._actions: List[up.engines.Action] = []
        self._inExecution: Set["up.model.fnode.FNode"] = set()

    def __repr__(self) -> str:
        s = []
        s.append(f"action combination {self.name}")
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
        s.append("  negative preconditions = [\n")
        for c in self.neg_preconditions:
            s.append(f"      {str(c)}\n")
        s.append("    ]\n")
        s.append("  positive preconditions = [\n")
        for c in self.pos_preconditions:
            s.append(f"      {str(c)}\n")
        s.append("    ]\n")
        s.append("  actions = [\n")
        for a in self.actions:
            s.append(f"      {str(a.name)}\n")
        s.append("    ]\n")
        s.append("  }")
        return "".join(s)

    @property
    def neg_preconditions(self):
        return self._neg_preconditions

    @property
    def pos_preconditions(self):
        return self._pos_preconditions

    @property
    def actions(self):
        return self._actions

    @property
    def inExecution(self):
        return self._inExecution

    def set_actions(self, actions: List["up.engines.Action"]):
        self._actions = actions.copy()

    def set_neg_preconditions(self, neg_preconditions: Set["up.model.fnode.FNode"]):
        self._neg_preconditions = neg_preconditions.copy()

    def set_pos_preconditions(self, pos_preconditions: Set["up.model.fnode.FNode"]):
        self._pos_preconditions = pos_preconditions.copy()

    def set_inExecution(self, inExecution: Set["up.model.fnode.FNode"]):
        self._inExecution = inExecution.copy()


class NoOpAction(Action):
    """ No Op action to allow the planner to choose do not act
    This action is relevant in the combination modulation """
    def __init__(
            self,
            _name: str,
            _parameters: Optional["OrderedDict[str, up.model.types.Type]"] = None,
            _env: Optional[Environment] = None,
            **kwargs: "up.model.types.Type",
    ):
        Action.__init__(self, _name, _parameters, _env, **kwargs)

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
        return "".join(s)

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, NoOpAction):
            return self._environment == oth._environment \
                    and self._name == oth._name \
                    and self._parameters == oth._parameters

    def __hash__(self) -> int:
        res = hash(self._name)
        for ap in self._parameters.items():
            res += hash(ap)
        return res