import unified_planning as up
from unified_planning.shortcuts import *

class Domain:
    def __init__(self, name, kind):
        self.problem = up.model.Problem(name)
        self.kind = kind

    def get_fluents(self, string):
        return [self.problem.fluent_by_name(s) for s in string]

    def get_objects(self, string):
        return [self.problem.object_by_name(s) for s in string]

    def use(self, action, fluent):
        action.add_precondition(StartPreconditionTiming(), fluent, True)
        action.add_start_effect(fluent, False)
        action.add_effect(fluent, True)

    def user_types(self):
        raise NotImplementedError

    def objects(self):
        raise NotImplementedError

    def fluents(self):
        raise NotImplementedError

    def actions(self):
        raise NotImplementedError

    def add_goal(self, deadline):
        raise NotImplementedError

    def set_initial_state(self):
        raise NotImplementedError

    def remove_actions(self, converted_problem):
        return
