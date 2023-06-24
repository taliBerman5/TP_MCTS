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
import functools
import operator


class Converted_problem:
    def __init__(
            self,
            _original_problem: "up.model.Problem",
    ):
        self._original_problem: "up.model.Problem" = _original_problem
        self._converted_problem: "up.model.Problem" = self._original_problem.clone()
        self._action_type: "up.model.UserType" = up.shortcuts.UserType('DurativeAction')
        self._inExecution: "up.model.Fluent" = up.model.Fluent('inExecution', up.shortcuts.BoolType(),
                                                               a=self._action_type)
        self._add_inExecution_fluent()
        self._split_durative_actions()
        self._convert_model_engine_actions()
        self._mutex_actions()


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
        for action in self._converted_problem._actions:

            if isinstance(action, up.model.DurativeAction):

                start_action = up.engine.InstantaneousStartAction("start_" + action._name)
                start_action._parameters = action._parameters

                # creating an object start_action for inExecution predicate
                object_start = up.model.Object("start-" + action.name, self._action_type)

                start_action._set_fixed_duration(action.duration)
                start_action._set_effects(action.during_effects)
                start_action.add_effect(self._inExecution(object_start), True)

                end_action = up.engine.InstantaneousAction("end_" + action._name)
                end_action._parameters = action._parameters
                end_action._set_effects(action.effects)
                end_action.add_effect(self._inExecution(object_start), False)
                end_action._set_probabilistic_effects(action.probabilistic_effects)

                start_action._set_end_action(end_action)

                # Add preconditions to start and end action
                for p_type in action.preconditions:
                    if p_type in {'START', 'OVERALL'}:
                        start_action.add_preconditions(action.preconditions[p_type])
                    if p_type in {'OVERALL', 'END'}:
                        end_action.add_preconditions(action.preconditions[p_type])

                end_action.add_precondition(self._inExecution(object_start), True)

                # Add to the problem the actions and the start action object
                self._converted_problem.add_object(object_start)
                self._converted_problem.add_action(start_action)
                self._converted_problem.add_action(end_action)

        # remove the durative actions and model.InstantaneousAction
        self._converted_problem._actions = [a for a in self._converted_problem._actions if
                                          not isinstance(a, up.model.DurativeAction)]

    def _convert_model_engine_actions(self):
        """
        convert instantaneous actions from `model` actions to be `engine` actions
        This is for convenient purposes - there is a split to negative and positive preconditions and effects

        """
        for action in self._converted_problem._actions:
            if isinstance(action, up.model.InstantaneousAction):
                engine_action = up.engine.InstantaneousAction(action._name)
                engine_action._parameters = action._parameters
                engine_action._set_preconditions(action.preconditions)
                engine_action._set_effects(action.effects)
                engine_action._set_probabilistic_effects(action.probabilistic_effects)

                self._converted_problem._remove_action(action)
                self._converted_problem.add_action(engine_action)

    def _mutex_actions(self):
        """
        Finding mutex actions and adding a precondition that they can't be executed in parallel

        Two actions are mutex if an OVERALL precondition of an durative action is in conflict with other action
        - During effect (only in durative actions)
        - Effect
        -Probabilistic effect

        If the conflicting action is also a durative action,
         - A precondition inExecution(start_action) is added to the start conflicting action
         - A precondition inExecution(start_conflicting_action) is added to the start action

        Otherwise, the conflicting action is instantaneous action
        - A precondition inExecution(start_action) is added to the conflicting action
        """
        for action in self._original_problem._actions:
            if isinstance(action, up.model.DurativeAction):
                for p_type in action.preconditions:
                    if p_type != 'OVERALL':
                        continue

                    for potential_action in self._original_problem._actions:
                        if potential_action == action:
                            continue
                        if self._check_mutex(action, potential_action):
                            self._adding_precondition_mutex_actions(action, potential_action)

    def _check_mutex(self, action, potential_action):
        """
        Check if two actions are mutex

        :param action: The checked action
        :param potential_action: The action is potentially in conflict with the preconditions of `action`

        :return: `True` if the actions are mutex else `False`
        """
        neg = self._negative_assignment(potential_action)
        pos = self._positive_assignment(potential_action)

        neg_mutex = any(x.fluent in neg and x.value.constant_value() for x in action.preconditions['OVERALL'])
        pos_mutex = any(x.fluent in pos and not x.value.constant_value() for x in action.preconditions['OVERALL'])

        if neg_mutex or pos_mutex:
            return True

        return False


    def _negative_assignment(self, action):
        """
        returns all the negative assignment of `action` to fluents in
        effects, during effect (if durative action) and probabilistic effects

        :param action: an action instance
        :return: The negative assignment of the actions in all kind of effects
        """
        neg = []
        if isinstance(action, up.model.DurativeAction):
            neg += [de.fluent for de in action.during_effects if not de.value.constant_value()]
        neg += [e.fluent for e in action.effects if not e.value.constant_value()]
        neg += functools.reduce(operator.iconcat, [pe.fluents for pe in action.probabilistic_effects], [])
        return neg

    def _positive_assignment(self, action):
        """
        returns all the positive assignment of `action` to fluents in
        effects, and during effect (if `action` is a durative action)

        :param action: an action instance
        :return: The negative assignment of the actions in effects and during effects
        """
        pos = []
        if isinstance(action, up.model.DurativeAction):
            pos += [de.fluent for de in action.during_effects if de.value.constant_value()]
        pos += [e.fluent for e in action.effects if e.value.constant_value()]

        return pos

    def _adding_precondition_mutex_actions(self, action, conflicting_action):
        """
        Adding to the actions a precondition that they would not be executed in parallel.

         If the conflicting action is also a durative action,
         - A precondition inExecution(start_action) is added to the start conflicting action
         - A precondition inExecution(start_conflicting_action) is added to the start action

        Otherwise, the conflicting action is instantaneous action
        - A precondition inExecution(start_action) is added to the conflicting action

        :param action:
        :param conflicting_action: The action is mutexed to `action`
        """
        start_action = self._converted_problem.action_by_name("start_" + action.name)


        if isinstance(conflicting_action, up.model.DurativeAction):
            start_conflicting_action = self._converted_problem.action_by_name("start_" + conflicting_action.name)

            start_action_object = self._converted_problem.object_by_name('start-'+action.name)
            start_conflicting_action.add_precondition(self._inExecution(start_action_object), False)

            start_conflicting_action_object = self._converted_problem.object_by_name('start-'+conflicting_action.name)
            start_action.add_precondition(self._inExecution(start_conflicting_action_object), False)

        else:
            conflicting_action = self._converted_problem.action_by_name(conflicting_action.name)
            start_action_object = self._converted_problem.object_by_name('start-' + action.name)
            conflicting_action.add_precondition(self._inExecution(start_action_object), False)