import unified_planning as up
import unified_planning.shortcuts
import functools
import operator
import itertools


class Convert_problem_combination:
    def __init__(
            self,
            _original_problem: "up.model.Problem",
    ):
        self._original_problem: "up.model.Problem" = _original_problem
        self._converted_problem: "up.model.Problem" = self._original_problem.clone()
        self._action_type: "up.model.UserType" = up.shortcuts.UserType('DurativeAction')
        self._inExecution: "up.model.Fluent" = up.model.Fluent('inExecution', up.shortcuts.BoolType(),
                                                               a=self._action_type)
        self._convert_model_engine_actions()
        self._add_inExecution_fluent()
        self._mutex_actions()
        self._combination_durative_actions()

    def __repr__(self) -> str:
        return self._converted_problem.__repr__()

    def __hash__(self) -> int:
        res = hash(self._original_problem)
        res += hash(self._converted_problem)
        res += hash(self._action_type)
        res += hash(self._inExecution)
        return res

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, Convert_problem_combination):
            return (
                    self._original_problem == oth._original_problem
                    and self._converted_problem == oth._converted_problem
                    and self._action_type == oth._action_type
                    and self._inExecution == oth._inExecution
            )
        else:
            return False

    @property
    def converted_problem(self):
        return self._converted_problem

    @property
    def original_problem(self):
        return self._original_problem

    def _add_inExecution_fluent(self):
        self._converted_problem.add_fluent(self._inExecution, default_initial_value=False)

    def _combination_durative_actions(self):
        """
        The function adds as an action all combinations of durative actions that can run in parallel.
        Action can run in parallel if they are not mutex.

        Mutex defenition:
        1. they have inconsistent preconditions
        2. an outcome of one action conflicts with an outcome of the other
        3. the precondition of one action conflicts with the (possibly probabilistic) effect of the other.
        4. the effect of one action possibly modifies a feature upon which another action’s transition function is conditioned upon.

        """
        durative_actions = [action for action in self._converted_problem._actions if
                            isinstance(action, up.engines.DurativeAction)]
        combs = []
        for i in range(2, len(durative_actions) + 1):
            els = [list(x) for x in itertools.combinations(durative_actions, i)]
            combs.extend(els)

        for combination in combs:
            neg_precondition = set()
            pos_precondition = set()
            action_execution = set()
            for action in combination:
                start_action_object = self._converted_problem.object_by_name('start-' + action.name)
                action_execution.add(self._inExecution(start_action_object))

                # remove the precondition of the execution of the current action
                # This precondition will be added to the combination precondition after the mutex check
                # An action is not mutex with itself
                temp_neg_pre = action.neg_preconditions.copy()
                temp_neg_pre.remove(self._inExecution(start_action_object))

                neg_precondition.update(temp_neg_pre.remove(self._inExecution(start_action_object)))
                pos_precondition.update(action.pos_preconditions)

            # check if all actions in the combination are not mutex
            if len(action_execution.intersection(neg_precondition)) == 0:
                comb_name = ",".join([action.name for action in combination])
                action_combination = up.engines.CombinationAction(comb_name)
                # adds execution actions to the precondition -
                # if one of the actions already in execution the combination can't be chosen
                neg_precondition.update(action_execution)
                action_combination.set_neg_preconditions(neg_precondition)
                action_combination.set_pos_preconditions(pos_precondition)
                action_combination.set_actions(combination)
                action_combination.set_inExecution(action_execution)
                self.converted_problem.add_action(action_combination)

    def _convert_model_engine_actions(self):
        """
        convert actions from `model` actions to be `engines` actions
        This is for convenient purposes - there is a split to negative and positive preconditions and effects

        """
        self._converted_problem.clear_actions()
        engine_action = None
        for action in self.original_problem._actions:
            if isinstance(action, up.model.InstantaneousAction):
                engine_action = up.engines.InstantaneousAction.init_from_action(action)

            if isinstance(action, up.model.DurativeAction):
                engine_action = up.engines.DurativeAction.init_from_action(action)

                # creating an object start_action for inExecution predicate
                object_start = up.model.Object("start-" + action.name, self._action_type)
                self._converted_problem.add_object(object_start)
                engine_action.set_inExecution(set(self._inExecution(object_start)))
                engine_action.add_precondition(self._inExecution(object_start), False)
                engine_action.add_effect(self._inExecution(object_start), False)

            self._converted_problem.add_action(engine_action)

    def _mutex_actions(self):
        """
        Finding mutex actions and adding a precondition that they can't be executed in parallel

        Two actions are mutex if on of the following holds -

        1. they have inconsistent preconditions
        2. an outcome of one action conflicts with an outcome of the other
        3. the precondition of one action conflicts with the (possibly probabilistic) effect of the other.
        4. the effect of one action possibly modifies a feature upon which another action’s transition function is conditioned upon.

        A precondition not inExecution(action) is added to the conflicting mutex action
        """
        for i in range(len(self.converted_problem._actions)):
            action = self.converted_problem._actions[i]
            for j in range(i + 1, len(self.converted_problem._actions)):
                potential_action = self.converted_problem._actions[j]
                if self._check_mutex(action, potential_action):
                    self._adding_precondition_mutex_actions(action, potential_action)

    def _check_mutex(self, action, potential_action):
        """
        Check if two actions are mutex

        :param action: The checked action
        :param potential_action: The action is potentially in mutex with `action`

        :return: `True` if the actions are mutex else `False`
        """
        # If both actions are instantaneous there no meaning of a parallel run
        if isinstance(action, up.model.InstantaneousAction) and isinstance(potential_action,
                                                                           up.model.InstantaneousAction):
            return False

        # Check inconsistent preconditions
        if len(potential_action.neg_preconditions.intersection(action.pos_preconditions)) > 0 or len(
                potential_action.pos_preconditions.intersection(action.neg_preconditions)) > 0:
            return True

        probabilistic = functools.reduce(operator.iconcat, [pe.fluents for pe in action.probabilistic_effects], [])
        potential_probabilistic = functools.reduce(operator.iconcat,
                                                   [pe.fluents for pe in potential_action.probabilistic_effects], [])

        neg_potential_effect = potential_action.del_effects.union(set(potential_probabilistic))
        pos_potential_effect = potential_action.add_effects.union(set(potential_probabilistic))
        neg_effect = action.del_effects.union(set(probabilistic))
        pos_effect = action.add_effects.union(set(probabilistic))

        # Check conflicting outcomes
        if len(neg_potential_effect.intersection(pos_effect)) > 0 or len(
                pos_potential_effect.intersection(neg_effect)) > 0:
            return True

        # Check conflicting precondition and effect
        if (len(neg_potential_effect.intersection(action.pos_preconditions)) > 0 or
                len(pos_potential_effect.intersection(action.neg_preconditions)) > 0 or
                len(neg_effect.intersection(potential_action.pos_preconditions)) > 0 or
                len(pos_effect.intersection(potential_action.neg_preconditions)) > 0):
            return True

        return False

    def _adding_precondition_mutex_actions(self, action, conflicting_action):
        """
        Adding to the `conflicting_action`, and `action` a precondition that they would not be executed in parallel.

         A precondition not inExecution(conflicting action) is added to the action
         A precondition not inExecution(action) is added to the conflicting action

        :param action:
        :param conflicting_action: The action is mutexed to `action`
        """

        start_action_object = self._converted_problem.object_by_name('start-' + action.name)
        start_conflicting_action_object = self._converted_problem.object_by_name('start-' + conflicting_action.name)

        # If the conflicting action is instantaneous it has no phase of execution
        # so there is no need of adding inExecution as a precondition to action
        if isinstance(conflicting_action, up.engines.DurativeAction):
            action.add_precondition(self._inExecution(start_conflicting_action_object), False)

        # If the action is instantaneous it has no phase of execution
        # so there is no need of adding inExecution as a precondition to the conflicting action
        if isinstance(action, up.engines.DurativeAction):
            conflicting_action.add_precondition(self._inExecution(start_action_object), False)
