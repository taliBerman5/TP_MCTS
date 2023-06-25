import unified_planning as up
class MDP:
    def __init__(self, problem: "up.model.problem.Preoblem", exploration_constant: float):
        self._problem = problem
        self._exploration_constant = exploration_constant


    @property
    def problem(self):
        return self._problem

    @property
    def exploration_constant(self):
        return self._exploration_constant

    def initial_state(self):
        """

        :return: the initial state of the problem
        """
        predicates = self.problem.initial_values
        pos_predicates = set([key for key, value in predicates.items() if value])
        return up.engine.State(pos_predicates)


    def is_terminal(self, state: "up.engine.state.State"): #TODO
        """
        Checks if all the goal predicates hold in the `state`
        and if all the timed goals achieved on time

        :param state: checked state
        :return: True is the `state` is a terminal state, False otherwise
        """
        self.problem.goals.issubset(state.predicates)
        # for self.problem.timed_goals.values:


        True


    def get_actions(self, state: "up.engine.state.State"):
        """
        If the positive preconditions of an action are true in the state
        and the negative preconditions of the action are false in the state
        The action is considered legal for the state

        :param state: the current state of the system
        :return: the legal actions that can be preformed in the state `state`
        """
        legal_actions = []
        for action in self.problem.actions:
            if action.pos_precondition.issubset(state.predicates) and \
                    action.pos_precondition.isdisjoint(state.predicates):

                legal_actions.append(action)

        return legal_actions