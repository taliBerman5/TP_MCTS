import unified_planning as up
from unified_planning.domains import Domain
from unified_planning.shortcuts import *


class Simple(Domain):
    def __init__(self, kind, deadline, object_amount=None, garbage_amount=0):
        Domain.__init__(self, f'simple_{garbage_amount}', kind)
        self.garbage_amount = garbage_amount
        self.userTypes = None
        self.user_types()
        self.objects()
        self.fluents()
        self.actions()
        self.add_goal(deadline)
        # self.set_initial_state()

    def user_types(self):
        Part = UserType('Part')
        self.userTypes = dict(Part=Part)

    def objects(self):
        """ Init parts """
        part_names = [str(i) for i in range(self.garbage_amount)]
        parts = [unified_planning.model.Object(p, self.userTypes['Part']) for p in part_names]
        self.problem.add_objects(parts)

    def fluents(self):
        got = unified_planning.model.Fluent('got', BoolType(), p=self.userTypes['Part'])
        self.problem.add_fluent(got, default_initial_value=False)

    def add_goal(self, deadline):
        got = self.problem.fluent_by_name('got')

        for obj in self.get_objects([str(i) for i in range(self.garbage_amount)]):
            self.problem.add_goal(got(obj))

        deadline_timing = Timing(delay=deadline, timepoint=Timepoint(TimepointKind.START))
        self.problem.set_deadline(deadline_timing)

    def actions(self):
        for i in range(self.garbage_amount):
            self.action(str(i))

    def action(self, obj_name):
        got = self.problem.fluent_by_name('got')
        obj = self.problem.object_by_name(obj_name)

        action = unified_planning.model.action.DurativeAction(f'action_{obj_name}')
        action.set_fixed_duration(4)

        action.add_effect(got(obj), True)
        self.problem.add_action(action)

