import unified_planning as up
from unified_planning.domains import Domain
from unified_planning.shortcuts import *


class Best_No_Parallel(Domain):
    def __init__(self, kind, deadline, object_amount=None, garbage_amount=None):
        Domain.__init__(self, 'strips', kind)
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
        part_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        parts = [unified_planning.model.Object(p, self.userTypes['Part']) for p in part_names]
        self.problem.add_objects(parts)

    def fluents(self):
        got = unified_planning.model.Fluent('got', BoolType(), p=self.userTypes['Part'])
        self.problem.add_fluent(got, default_initial_value=False)

    def add_goal(self, deadline):
        got = self.problem.fluent_by_name('got')
        a, b, c, d, e, f, g, h = self.get_objects(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])

        self.problem.add_goal(got(a))
        self.problem.add_goal(got(b))
        self.problem.add_goal(got(c))
        self.problem.add_goal(got(d))
        self.problem.add_goal(got(e))
        self.problem.add_goal(got(f))
        self.problem.add_goal(got(g))
        self.problem.add_goal(got(h))

        deadline_timing = Timing(delay=deadline, timepoint=Timepoint(TimepointKind.START))
        self.problem.set_deadline(deadline_timing)

    def actions(self):
        self.a_action()
        self.b_action()
        self.c_action()
        self.d_action()
        self.e_action()
        self.f_action()
        self.g_action()
        self.h_action()


    def a_action(self):
        got = self.problem.fluent_by_name('got')
        a = self.problem.object_by_name('a')

        action_a = unified_planning.model.action.DurativeAction('action_a')
        action_a.set_fixed_duration(4)

        action_a.add_effect(got(a), True)
        self.problem.add_action(action_a)


    def b_action(self):
        got = self.problem.fluent_by_name('got')
        b = self.problem.object_by_name('b')

        action_b = unified_planning.model.action.DurativeAction('action_b')
        action_b.set_fixed_duration(4)

        action_b.add_effect(got(b), True)
        self.problem.add_action(action_b)


    def c_action(self):
        got = self.problem.fluent_by_name('got')
        c = self.problem.object_by_name('c')

        action_c = unified_planning.model.action.DurativeAction('action_c')
        action_c.set_fixed_duration(2)

        action_c.add_effect(got(c), True)
        self.problem.add_action(action_c)


    def d_action(self):
        got = self.problem.fluent_by_name('got')
        d = self.problem.object_by_name('d')

        action_d = unified_planning.model.action.DurativeAction('action_d')
        action_d.set_fixed_duration(2)

        action_d.add_effect(got(d), True)
        self.problem.add_action(action_d)

    def e_action(self):
        got = self.problem.fluent_by_name('got')
        a, b, c, d, e = self.get_objects(['a', 'b', 'c', 'd', 'e'])

        action_e = unified_planning.model.action.DurativeAction('action_e')
        action_e.set_fixed_duration(2)

        action_e.add_precondition(StartPreconditionTiming(), got(c), True)
        action_e.add_precondition(StartPreconditionTiming(), got(d), True)
        action_e.add_effect(got(e), True)
        action_e.add_effect(got(a), False)
        action_e.add_effect(got(b), False)
        self.problem.add_action(action_e)


    def f_action(self):
        got = self.problem.fluent_by_name('got')
        a, b, c, d, f = self.get_objects(['a', 'b', 'c', 'd', 'f'])

        action_f = unified_planning.model.action.DurativeAction('action_f')
        action_f.set_fixed_duration(2)

        action_f.add_precondition(StartPreconditionTiming(), got(c), True)
        action_f.add_precondition(StartPreconditionTiming(), got(d), True)
        action_f.add_effect(got(f), True)
        action_f.add_effect(got(a), False)
        action_f.add_effect(got(b), False)
        self.problem.add_action(action_f)

    def g_action(self):
        got = self.problem.fluent_by_name('got')
        e, f, g = self.get_objects(['e', 'f', 'g'])

        action_g = unified_planning.model.action.DurativeAction('action_g')
        action_g.set_fixed_duration(2)

        action_g.add_precondition(StartPreconditionTiming(), got(e), True)
        action_g.add_precondition(StartPreconditionTiming(), got(f), True)
        action_g.add_effect(got(g), True)
        self.problem.add_action(action_g)


    def h_action(self):
        got = self.problem.fluent_by_name('got')
        e, f, h = self.get_objects(['e', 'f', 'h'])

        action_h = unified_planning.model.action.DurativeAction('action_h')
        action_h.set_fixed_duration(2)

        action_h.add_precondition(StartPreconditionTiming(), got(e), True)
        action_h.add_precondition(StartPreconditionTiming(), got(f), True)
        action_h.add_effect(got(h), True)
        self.problem.add_action(action_h)

