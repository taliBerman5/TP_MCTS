import unified_planning as up
import unified_planning.shortcuts
import functools
import operator


class Convert_problem:
    def __init__(
            self,
            _original_problem: "up.model.Problem",
    ):
        self._original_problem: "up.model.Problem" = _original_problem
        self._converted_problem: "up.model.Problem" = self._original_problem.clone()
        self._action_type: "up.model.UserType" = up.shortcuts.UserType('DurativeAction')
        self._inExecution: "up.model.Fluent" = up.model.Fluent('inExecution', up.shortcuts.BoolType(),
                                                               a=self._action_type)
        self._grounded_actions = []
        self._add_inExecution_fluent()
        self._split_durative_actions()
        self._convert_model_engine_actions()
        self._mutex_actions()

    def __repr__(self) -> str:
        return self._converted_problem.__repr__()

    def __hash__(self) -> int:
        res = hash(self._original_problem)
        res += hash(self._converted_problem)
        res += hash(self._action_type)
        res += hash(self._inExecution)
        return res

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, Convert_problem):
            return  (
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

                start_action = up.engines.InstantaneousStartAction("start_" + action._name)
                start_action._parameters = action._parameters

                # creating an object start_action for inExecution predicate
                object_start = up.model.Object("start-" + action.name, self._action_type)

                start_action._set_fixed_duration(action.duration)
                start_action._set_effects(action.start_effects)
                start_action.add_effect(self._inExecution(object_start), True)
                start_action.add_precondition(self._inExecution(object_start), False)

                end_action = up.engines.InstantaneousEndAction("end_" + action._name)
                end_action._parameters = action._parameters
                end_action._set_effects(action.effects)
                end_action.add_effect(self._inExecution(object_start), False)
                end_action._set_probabilistic_effects(action.probabilistic_effects)

                start_action._set_end_action(end_action)
                end_action._set_start_action(start_action)

                # Add preconditions to start and end action
                for p_type in action.preconditions:
                    if p_type == 'START':
                        start_action.add_preconditions(action.preconditions[p_type])
                    if p_type == 'OVERALL':
                        # If the there is a start effect that satisfies an over all precondition it shouldn't be added
                        # to the preconditions
                        oa_p = [p for p in action.preconditions[p_type] if all(not p.same_effect(e) for e in action.start_effects)]
                        start_action.add_preconditions(oa_p)

                    if p_type == 'END':
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
        convert instantaneous actions from `model` actions to be `engines` actions
        This is for convenient purposes - there is a split to negative and positive preconditions and effects

        """
        remove = []
        add = []
        for action in self._converted_problem._actions:
            if isinstance(action, up.model.InstantaneousAction):
                engine_action = up.engines.InstantaneousAction(action._name)
                engine_action._parameters = action._parameters
                engine_action._set_preconditions(action.preconditions)
                engine_action._set_effects(action.effects)
                engine_action._set_probabilistic_effects(action.probabilistic_effects)

                remove.append(action)
                add.append(engine_action)

        for i in range(len(remove)):
            self._converted_problem._remove_action(remove[i])
            self._converted_problem.add_action(add[i])



    def _mutex_actions(self):
        """
        Finding mutex actions and adding a precondition that they can't be executed in parallel
        Finding soft mutex actions and adding to the end action those actions

        Two actions are mutex if an OVERALL precondition of an durative action is in conflict with other action
        - During effect (only in durative actions)

        Action a is soft mutex with action b if and OVERALL precondition of action a is in conflict with action's b
        - Effect
        -Probabilistic effect

        A precondition inExecution(start_action) is added to the conflicting mutex action
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
                        if self._check_soft_mutex(action, potential_action):
                            self._adding_soft_mutex_actions(action, potential_action)

    def _check_mutex(self, action, potential_action):
        """
        Check if two actions are mutex

        :param action: The checked action
        :param potential_action: The action is potentially in conflict with the preconditions of `action`

        :return: `True` if the actions are mutex else `False`
        """
        neg = self._negative_start_assignment(potential_action)
        pos = self._positive_start_assignment(potential_action)

        neg_mutex = any(x.fluent in neg and x.value.constant_value() for x in action.preconditions['OVERALL'])
        pos_mutex = any(x.fluent in pos and not x.value.constant_value() for x in action.preconditions['OVERALL'])

        if neg_mutex or pos_mutex:
            return True

        return False


    def _check_soft_mutex(self, action, potential_action):
        """
        Check if two actions are soft mutex

        :param action: The checked action
        :param potential_action: The action is potentially in conflict with the preconditions of `action`

        :return: `True` if the actions are soft mutex else `False`
        """
        neg = self._negative_end_assignment(potential_action)
        pos = self._positive_end_assignment(potential_action)

        neg_mutex = any(x.fluent in neg and x.value.constant_value() for x in action.preconditions['OVERALL'])
        pos_mutex = any(x.fluent in pos and not x.value.constant_value() for x in action.preconditions['OVERALL'])

        if neg_mutex or pos_mutex:
            return True

        return False


    def _negative_end_assignment(self, action):
        """
        returns all the negative end assignments of durative `action` to fluents in
        effects, and probabilistic effects

        :param action: an action instance
        :return: The negative end assignments of the actions
        """
        neg = []
        if isinstance(action, up.model.DurativeAction):
            neg += [e.fluent for e in action.effects if not e.value.constant_value()]
            neg += functools.reduce(operator.iconcat, [pe.fluents for pe in action.probabilistic_effects], [])
        return neg


    def _negative_start_assignment(self, action):
        """
        returns all the negative start assignments of `action` to fluents in
        if durative action - during effect
        else effects and probabilistic effects

        :param action: an action instance
        :return: The negative start assignments of the actions
        """
        neg = []
        if isinstance(action, up.model.DurativeAction):
            neg += [de.fluent for de in action.start_effects if not de.value.constant_value()]
        else:
            neg += [e.fluent for e in action.effects if not e.value.constant_value()]
            neg += functools.reduce(operator.iconcat, [pe.fluents for pe in action.probabilistic_effects], [])
        return neg

    def _positive_start_assignment(self, action):
        """
        returns all the positive start assignments of `action` to fluents
        if durative action - during effect
        else effects and probabilistic effects

        :param action: an action instance
        :return: The positive start assignments of the actions
        """
        pos = []
        if isinstance(action, up.model.DurativeAction):
            pos += [de.fluent for de in action.start_effects if de.value.constant_value()]
        else:
            pos += [e.fluent for e in action.effects if e.value.constant_value()]
            pos += functools.reduce(operator.iconcat, [pe.fluents for pe in action.probabilistic_effects], [])
        return pos

    def _positive_end_assignment(self, action):
        """
        returns all the positive end assignments of durative `action` to fluents in
        effects, and probabilistic effects

        :param action: an action instance
        :return: The positive assignment of the actions in effects and during effects
        """
        pos = []
        if isinstance(action, up.model.DurativeAction):
            pos += [e.fluent for e in action.effects if e.value.constant_value()]
            pos += functools.reduce(operator.iconcat, [pe.fluents for pe in action.probabilistic_effects], [])
        return pos

    def _adding_precondition_mutex_actions(self, action, conflicting_action):
        """
        Adding to the `conflicting_action` a precondition that they would not be executed in parallel.

         A precondition inExecution(start_action) is added to the conflicting action

        :param action:
        :param conflicting_action: The action is mutexed to `action`
        """
        start_action_object = self._converted_problem.object_by_name('start-' + action.name)

        if isinstance(conflicting_action, up.model.DurativeAction):
            start_conflicting_action = self._converted_problem.action_by_name("start_" + conflicting_action.name)
            start_conflicting_action.add_precondition(self._inExecution(start_action_object), False)

        else:
            conflicting_action = self._converted_problem.action_by_name(conflicting_action.name)
            conflicting_action.add_precondition(self._inExecution(start_action_object), False)

    def _adding_soft_mutex_actions(self, action, conflicting_action):
        """
        Adding to the `conflicting_action` a precondition that they would not be executed in parallel.

         A precondition inExecution(start_action) is added to the conflicting action

        :param action:
        :param conflicting_action: The action is mutexed to `action`
        """

        start_action_object = self._converted_problem.object_by_name('start-' + action.name)

        end_conflicting_action = self._converted_problem.action_by_name("end_" + conflicting_action.name)
        end_conflicting_action.add_precondition(self._inExecution(start_action_object), False)


