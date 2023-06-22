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


class Converted_problem:
    def __init__(
            self,
            _original_problem: "up.model.Problem",
    ):
        self._original_problem: "up.model.Problem" = _original_problem
        self._converted_problem: "up.model.Problem" = self._clone_except_durative_actions()
        self._action_type: "up.model.UserType" = up.shortcuts.UserType('DurativeAction')
        self._inExecution: "up.model.Fluent" = up.model.Fluent('inExecution', up.shortcuts.BoolType(),
                                                               a=self._action_type)

        self._add_inExecution_fluent()
        self._split_durative_actions()

    def _clone_except_durative_actions(self):
        converted_problem = self._original_problem.clone()
        converted_problem._actions = [a for a in converted_problem._actions if
                                      not isinstance(a, up.model.DurativeAction)]
        return converted_problem

    def _add_inExecution_fluent(self):
        self._converted_problem.add_fluent(self._inExecution, default_initial_value=False)

    def _split_durative_actions(self):
        """
        The function adds to the converted problem start and end actions representing each durative action

        Start action -
        Preconditions: the START and OVERALL preconditions of the original action
        Effects: the during effects of the original action, and inExection(start-action) for the relevant action

        End action -
        Preconditions: the END and OVERALL preconditions of the original action
        Effects: the effects of the original action, and not inExection(start-action) for the relevant action
        Probabilistic Effects: the probabilistic effects of the original action

        """
        for action in self._original_problem._actions:
            if isinstance(action, up.model.DurativeAction):

                start_action = up.model.InstantaneousStartAction("start_" + action._name)
                start_action._parameters = action._parameters

                # creating an object start_action for inExecution predicate
                object_start = up.model.Object("start-" + action.name, self._action_type)

                start_action._set_fixed_duration(action.duration)
                start_action._set_effects(action.during_effects)
                start_action.add_effect(self._inExecution(object_start), True)

                end_action = up.model.InstantaneousAction("end_" + action._name)
                end_action._parameters = action._parameters
                end_action._set_effects(action.effects)
                end_action.add_effect(self._inExecution(object_start), False)
                end_action._set_probabilistic_effects(action.probabilistic_effects)

                start_action._set_end_action(end_action)

                # Add preconditions to start and end action
                for p_type in action.preconditions:
                    if p_type in {'START', 'OVERALL'}:
                        start_action._preconditions += action.preconditions[p_type]
                    if p_type in {'OVERALL', 'END'}:
                        end_action._preconditions += action.preconditions[p_type]

                end_action.add_precondition(self._inExecution(object_start))

                # Add to the problem the actions and the start action object
                self._converted_problem.add_object(object_start)
                self._converted_problem.add_action(start_action)
                self._converted_problem.add_action(end_action)

        print(5)
