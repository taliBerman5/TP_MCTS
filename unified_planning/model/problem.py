# Copyright 2021 AIPlan4EU project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""This module defines the problem class."""


import unified_planning as up
from unified_planning.model.abstract_problem import AbstractProblem
from unified_planning.model.mixins import (
    ActionsSetMixin,
    FluentsSetMixin,
    ObjectsSetMixin,
    UserTypesSetMixin,
    InitialStateMixin,
    # MetricsMixin,
)
from unified_planning.model.expression import ConstantExpression
from unified_planning.exceptions import (
    UPProblemDefinitionError,
    UPTypeError,
    UPConflictingEffectsException,
)
from fractions import Fraction
from typing import Optional, List, Dict, Set, Tuple, Union, cast


class Problem(  # type: ignore[misc]
    AbstractProblem,
    UserTypesSetMixin,
    FluentsSetMixin,
    ActionsSetMixin,
    ObjectsSetMixin,
    InitialStateMixin,
):
    """
    Represents the classical planning problem, with :class:`Actions <unified_planning.model.Action>`, :class:`Fluents <unified_planning.model.Fluent>`, :class:`Objects <unified_planning.model.Object>` and :class:`UserTypes <unified_planning.model.Type>`.

    The `Actions` can be :class:`DurativeActions <unified_planning.model.DurativeAction>` when the `Problem` deals with time.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        environment: Optional["up.environment.Environment"] = None,
        *,
        initial_defaults: Dict["up.model.types.Type", "ConstantExpression"] = {},
    ):
        AbstractProblem.__init__(self, name, environment)
        UserTypesSetMixin.__init__(self, self.environment, self.has_name)
        FluentsSetMixin.__init__(
            self, self.environment, self._add_user_type, self.has_name, initial_defaults
        )
        ActionsSetMixin.__init__(
            self, self.environment, self._add_user_type, self.has_name
        )
        ObjectsSetMixin.__init__(
            self, self.environment, self._add_user_type, self.has_name
        )
        InitialStateMixin.__init__(self, self, self, self.environment)
        # MetricsMixin.__init__(self, self.environment)
        self._operators_extractor = up.model.walkers.OperatorsExtractor()
        self._timed_effects: Dict[
            "up.model.timing.Timing", List["up.model.effect.Effect"]
        ] = {}
        self._timed_goals: Dict[
            "up.model.timing.TimeInterval", List["up.model.fnode.FNode"]
        ] = {}
        self._trajectory_constraints: List["up.model.fnode.FNode"] = list()
        self._goals: List["up.model.fnode.FNode"] = list()
        self._deadline: Union["up.model.timing.Timing", "up.model.timing.TimeInterval"] = None

    def __repr__(self) -> str:
        s = []
        if self.name is not None:
            s.append(f"problem name = {str(self.name)}\n\n")
        if len(self.user_types) > 0:
            s.append(f"types = {str(list(self.user_types))}\n\n")
        s.append("fluents = [\n")
        for f in self.fluents:
            s.append(f"  {str(f)}\n")
        s.append("]\n\n")
        s.append("actions = [\n")
        for a in self.actions:
            s.append(f"  {str(a)}\n")
        s.append("]\n\n")
        if len(self.user_types) > 0:
            s.append("objects = [\n")
            for ty in self.user_types:
                s.append(f"  {str(ty)}: {str(list(self.objects(ty)))}\n")
            s.append("]\n\n")
        s.append("initial fluents default = [\n")
        for f in self._fluents:
            if f in self._fluents_defaults:
                v = self._fluents_defaults[f]
                s.append(f"  {str(f)} := {str(v)}\n")
        s.append("]\n\n")
        s.append("initial values = [\n")
        for k, v in self.explicit_initial_values.items():
            s.append(f"  {str(k)} := {str(v)}\n")
        s.append("]\n\n")
        if len(self.timed_effects) > 0:
            s.append("timed effects = [\n")
            for t, el in self.timed_effects.items():
                s.append(f"  {str(t)} :\n")
                for e in el:
                    s.append(f"    {str(e)}\n")
            s.append("]\n\n")
        if len(self.timed_goals) > 0:
            s.append("timed goals = [\n")
            for i, gl in self.timed_goals.items():
                s.append(f"  {str(i)} :\n")
                for g in gl:
                    s.append(f"    {str(g)}\n")
            s.append("]\n\n")
        s.append("goals = [\n")
        for g in self.goals:
            s.append(f"  {str(g)}\n")
        s.append("]\n\n")
        if self.deadline:
            s.append(f"deadline = {self.deadline}")
        if self.trajectory_constraints:
            s.append("trajectory constraints = [\n")
            for c in self.trajectory_constraints:
                s.append(f"  {str(c)}\n")
            s.append("]\n\n")

        return "".join(s)

    def __eq__(self, oth: object) -> bool:
        if not (isinstance(oth, Problem)) or self._env != oth._env:
            return False

        if not UserTypesSetMixin.__eq__(self, oth):
            return False
        if not ObjectsSetMixin.__eq__(self, oth):
            return False
        if not FluentsSetMixin.__eq__(self, oth):
            return False
        if not InitialStateMixin.__eq__(self, oth):
            return False

        if set(self._goals) != set(oth._goals):
            return False
        if set(self._actions) != set(oth._actions):
            return False
        if set(self._trajectory_constraints) != set(oth._trajectory_constraints):
            return False

        if len(self._timed_effects) != len(oth._timed_effects):
            return False
        for t, tel in self._timed_effects.items():
            oth_tel = oth._timed_effects.get(t, None)
            if oth_tel is None:
                return False
            elif set(tel) != set(oth_tel):
                return False
        if len(self._timed_goals) != len(oth._timed_goals):
            return False
        for i, tgl in self._timed_goals.items():
            oth_tgl = oth._timed_goals.get(i, None)
            if oth_tgl is None:
                return False
            elif set(tgl) != set(oth_tgl):
                return False
        if self._deadline != oth._deadline:
            return False
        return True

    def __hash__(self) -> int:
        res = hash(self._name)

        res += FluentsSetMixin.__hash__(self)
        res += ObjectsSetMixin.__hash__(self)
        res += UserTypesSetMixin.__hash__(self)
        res += InitialStateMixin.__hash__(self)

        for a in self._actions:
            res += hash(a)
        for c in self._trajectory_constraints:
            res += hash(c)
        for t, el in self._timed_effects.items():
            res += hash(t)
            for e in set(el):
                res += hash(e)
        for i, gl in self._timed_goals.items():
            res += hash(i)
            for g in set(gl):
                res += hash(g)
        for g in self._goals:
            res += hash(g)
        res += hash(self._deadline)
        return res

    def clone(self):
        new_p = Problem(self._name, self._env)
        UserTypesSetMixin._clone_to(self, new_p)
        ObjectsSetMixin._clone_to(self, new_p)
        FluentsSetMixin._clone_to(self, new_p)
        InitialStateMixin._clone_to(self, new_p)

        new_p._actions = [a.clone() for a in self._actions]
        new_p._timed_effects = {
            t: [e.clone() for e in el] for t, el in self._timed_effects.items()
        }
        new_p._timed_goals = {i: [g for g in gl] for i, gl in self._timed_goals.items()}
        new_p._goals = self._goals[:]
        new_p._trajectory_constraints = self._trajectory_constraints[:]
        new_p._deadline = self._deadline

        # last as it requires actions to be cloned already
        return new_p

    def has_name(self, name: str) -> bool:
        """
        Returns `True` if the given `name` is already in the `Problem`, `False` otherwise.

        :param name: The target name to find in the `Problem`.
        :return: `True` if the given `name` is already in the `Problem`, `False` otherwise."""
        return (
            self.has_action(name)
            or self.has_fluent(name)
            or self.has_object(name)
            or self.has_type(name)
        )

    def normalize_plan(self, plan: "up.plans.Plan") -> "up.plans.Plan":
        """
        Normalizes the given `Plan`, that is potentially the result of another
        `Problem`, updating the :class:`~unified_planning.model.Object` references present in it with the ones of
        this `Problem` which are syntactically equal.

        :param plan: The `Plan` that must be normalized.
        :return: A `Plan` syntactically valid for this `Problem`.
        """
        return plan.replace_action_instances(self._replace_action_instance)

    def _replace_action_instance(
        self, action_instance: "up.plans.ActionInstance"
    ) -> "up.plans.ActionInstance":
        em = self.environment.expression_manager
        new_a = self.action(action_instance.action.name)
        params = []
        for p in action_instance.actual_parameters:
            if p.is_object_exp():
                obj = self.object(p.object().name)
                params.append(em.ObjectExp(obj))
            elif p.is_bool_constant():
                params.append(em.Bool(p.is_true()))
            elif p.is_int_constant():
                params.append(em.Int(cast(int, p.constant_value())))
            elif p.is_real_constant():
                params.append(em.Real(cast(Fraction, p.constant_value())))
            else:
                raise NotImplementedError
        return up.plans.ActionInstance(new_a, tuple(params))

    def _remove_action(self, action: "up.model.action.Action"):
        if action in self.actions:
            self.actions.remove(action)

    def get_static_fluents(self) -> Set["up.model.fluent.Fluent"]:
        """
        Returns the set of the `static fluents`.

        `Static fluents` are those who can't change their values because they never
        appear in the :func:`fluent <unified_planning.model.Effect.fluent>` field of an `Effect`, therefore there are no :func:`Actions <unified_planning.model.Problem.actions>`
        in the `Problem` that can change their value.
        """
        static_fluents: Set["up.model.fluent.Fluent"] = set(self._fluents)
        for a in self._actions:
            if isinstance(a, up.model.action.InstantaneousAction):
                for e in a.effects:
                    static_fluents.discard(e.fluent.fluent())
                for pe in a.probabilistic_effects:
                    for f in pe.fluents:
                        static_fluents.discard(f.fluent())
            elif isinstance(a, up.model.action.DurativeAction):
                for e in a.start_effects:
                    static_fluents.discard(e.fluent.fluent())
                for e in a.effects:
                    static_fluents.discard(e.fluent.fluent())
                for pe in a.probabilistic_effects:
                    for f in pe.fluents:
                        static_fluents.discard(f.fluent())
            else:
                raise NotImplementedError
        for el in self._timed_effects.values():
            for e in el:
                if e.fluent.fluent() in static_fluents:
                    static_fluents.remove(e.fluent.fluent())
        return static_fluents

    def set_deadline(
        self,
        interval: Union["up.model.timing.Timing", "up.model.timing.TimeInterval"],
    ):
        """
        Adds a deadline to the `Problem`.

        :param interval: The interval of time in which the goals of the problem must be `True`.

        """
        if isinstance(interval, up.model.Timing):
            interval = up.model.TimePointInterval(interval)
        if (interval.lower.is_from_end() and interval.lower.delay > 0) or (
            interval.upper.is_from_end() and interval.upper.delay > 0
        ):
            raise UPProblemDefinitionError(
                "Problem timing can not be `end - k` with k > 0."
            )
        self._deadline = interval

    @property
    def deadline(self):
        """
        A deadline to the time when all goals of the problem must be True
        :return: The `deadline` of the problem
        """
        return self._deadline
    def add_timed_goal(
        self,
        interval: Union["up.model.timing.Timing", "up.model.timing.TimeInterval"],
        goal: Union["up.model.fnode.FNode", "up.model.fluent.Fluent", bool],
    ):
        """
        Adds the `timed goal` to the `Problem`. A `timed goal` is a `goal` that must be satisfied in a
        given period of time.

        :param interval: The interval of time in which the given goal must be `True`.
        :param goal: The expression that must be evaluated to `True` in the given `interval`.
        """
        assert (
            isinstance(goal, bool) or goal.environment == self._env
        ), "timed_goal does not have the same environment of the problem"
        if isinstance(interval, up.model.Timing):
            interval = up.model.TimePointInterval(interval)
        if (interval.lower.is_from_end() and interval.lower.delay > 0) or (
            interval.upper.is_from_end() and interval.upper.delay > 0
        ):
            raise UPProblemDefinitionError(
                "Problem timing can not be `end - k` with k > 0."
            )
        (goal_exp,) = self._env.expression_manager.auto_promote(goal)
        assert self._env.type_checker.get_type(goal_exp).is_bool_type()
        goals = self._timed_goals.setdefault(interval, [])
        if goal_exp not in goals:
            goals.append(goal_exp)

    @property
    def timed_goals(
        self,
    ) -> Dict["up.model.timing.TimeInterval", List["up.model.fnode.FNode"]]:
        """Returns all the `timed goals` in the `Problem`."""
        return self._timed_goals

    def clear_timed_goals(self):
        """Removes all the `timed goals` from the `Problem`."""
        self._timed_goals = {}

    def add_timed_effect(
        self,
        timing: "up.model.timing.Timing",
        fluent: Union["up.model.fnode.FNode", "up.model.fluent.Fluent"],
        value: "up.model.expression.Expression",
        condition: "up.model.expression.BoolExpression" = True,
    ):
        """
        Adds the given `timed effect` to the `Problem`; a `timed effect` is an :class:`~unified_planning.model.Effect` applied at a fixed time.

        :param timing: The exact time in which the given `Effect` is applied.
        :param fluent: The fluent modified by the `Effect`.
        :param value: The value assigned to the given `fluent` at the given `time`.
        :param condition: The condition that must be evaluated to `True` in order for this `Effect` to be
            actually applied.
        """
        if timing.is_from_end():
            raise UPProblemDefinitionError(
                f"Timing used in timed effect cannot be EndTiming."
            )
        (
            fluent_exp,
            value_exp,
            condition_exp,
        ) = self._env.expression_manager.auto_promote(fluent, value, condition)
        assert fluent_exp.is_fluent_exp()
        if not self._env.type_checker.get_type(condition_exp).is_bool_type():
            raise UPTypeError("Effect condition is not a Boolean condition!")
        if not fluent_exp.type.is_compatible(value_exp.type):
            raise UPTypeError("Timed effect has not compatible types!")
        self._add_effect_instance(
            timing, up.model.effect.Effect(fluent_exp, value_exp, condition_exp)
        )

    def _add_effect_instance(
        self, timing: "up.model.timing.Timing", effect: "up.model.effect.Effect"
    ):
        assert (
            effect.environment == self._env
        ), "effect does not have the same environment of the problem"

        up.model.effect.check_conflicting_effects(
            effect,
            timing,
            "problem",
        )
        self._timed_effects.setdefault(timing, []).append(effect)

    @property
    def timed_effects(
        self,
    ) -> Dict["up.model.timing.Timing", List["up.model.effect.Effect"]]:
        """Returns all the `timed effects` in the `Problem`."""
        return self._timed_effects

    def clear_timed_effects(self):
        """Removes all the `timed effects` from the `Problem`."""
        self._timed_effects = {}


    def add_goal(
        self, goal: Union["up.model.fnode.FNode", "up.model.fluent.Fluent", bool]
    ):
        """
        Adds the given `goal` to the `Problem`; a goal is an expression that must be evaluated to `True` at the
        end of the execution of a :class:`~unified_planning.plans.Plan`. If a `Plan` does not satisfy all the given `goals`, it is not valid.

        :param goal: The expression added to the `Problem` :func:`goals <unified_planning.model.Problem.goals>`.
        """
        assert (
            isinstance(goal, bool) or goal.environment == self._env
        ), "goal does not have the same environment of the problem"
        (goal_exp,) = self._env.expression_manager.auto_promote(goal)
        assert self._env.type_checker.get_type(goal_exp).is_bool_type()
        if goal_exp != self._env.expression_manager.TRUE():
            self._goals.append(goal_exp)

    def add_trajectory_constraint(self, constraint: "up.model.fnode.FNode"):
        """
        Adds the given `trajectory_constraint` to the `Problem`;
        a trajectory_constraint is an expression defined as:
        Always, Sometime, At-Most-Once, Sometime-Before, Sometime-After or
        defined with universal quantifiers.
        Nesting of these temporal operators is forbidden.

        :param trajectory_constraint: The expression added to the `Problem`.
        """
        if constraint.is_and() or constraint.is_forall():
            for arg in constraint.args:
                assert (
                    arg.is_sometime()
                    or arg.is_sometime_after()
                    or arg.is_sometime_before()
                    or arg.is_at_most_once()
                    or arg.is_always()
                ), "trajectory constraint not in the correct form"
        else:
            assert (
                constraint.is_sometime()
                or constraint.is_sometime_after()
                or constraint.is_sometime_before()
                or constraint.is_at_most_once()
                or constraint.is_always()
            ), "trajectory constraint not in the correct form"
        self._trajectory_constraints.append(constraint.simplify())

    @property
    def goals(self) -> List["up.model.fnode.FNode"]:
        """Returns all the `goals` in the `Problem`."""
        return self._goals

    @property
    def trajectory_constraints(self) -> List["up.model.fnode.FNode"]:
        """Returns the 'trajectory_constraints' in the 'Problem'."""
        return self._trajectory_constraints

    def clear_goals(self):
        """Removes all the `goals` from the `Problem`."""
        self._goals = []

    def clear_trajectory_constraints(self):
        """Removes the trajectory_constraints."""
        self._trajectory_constraints = []

    def get_fluent_exp(self, fluent: "up.model.fluent.Fluent"):
        return self.environment.expression_manager.auto_promote(fluent)[0]

    def get_fluents_exp(self, fluents: List["up.model.fluent.Fluent"]):
        return self.environment.expression_manager.auto_promote(fluents)



