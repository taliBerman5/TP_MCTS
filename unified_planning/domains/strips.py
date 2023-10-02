import unified_planning as up
from unified_planning.domains import Domain
from unified_planning.shortcuts import *


class Strips(Domain):
    def __init__(self, kind, deadline, garbage_amount=None):
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
        part_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        parts = [unified_planning.model.Object(p, self.userTypes['Part']) for p in part_names]
        self.problem.add_objects(parts)

    def fluents(self):
        got = unified_planning.model.Fluent('got', BoolType(), p=self.userTypes['Part'])
        self.problem.add_fluent(got, default_initial_value=False)

    def add_goal(self, deadline):
        got = self.problem.fluent_by_name('got')
        a, b, c, d, e, f, g, h, i= self.get_objects(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'])

        self.problem.add_goal(got(a))
        self.problem.add_goal(got(b))
        self.problem.add_goal(got(c))
        self.problem.add_goal(got(d))
        self.problem.add_goal(got(e))
        self.problem.add_goal(got(f))
        self.problem.add_goal(got(g))
        self.problem.add_goal(got(h))
        self.problem.add_goal(got(i))

        deadline_timing = Timing(delay=deadline, timepoint=Timepoint(TimepointKind.START))
        self.problem.set_deadline(deadline_timing)

    def actions(self):
        self.nine_action()
        self.four1_action()
        self.two1_action()
        self.two2_action()
        self.one1_action()
        self.one2_action()
        self.one3_action()
        self.one4_action()
        self.one5_action()

    def nine_action(self):
        got = self.problem.fluent_by_name('got')
        a = self.problem.object_by_name('a')

        nine = unified_planning.model.action.DurativeAction('nine')
        nine.set_fixed_duration(9)

        nine.add_effect(got(a), True)
        self.problem.add_action(nine)

    def four1_action(self):
        got = self.problem.fluent_by_name('got')
        b = self.problem.object_by_name('b')

        four1 = unified_planning.model.action.DurativeAction('four1')
        four1.set_fixed_duration(4)

        four1.add_effect(got(b), True)
        self.problem.add_action(four1)

    def two1_action(self):
        got = self.problem.fluent_by_name('got')
        c = self.problem.object_by_name('c')

        two1 = unified_planning.model.action.DurativeAction('two1')
        two1.set_fixed_duration(2)

        two1.add_effect(got(c), True)
        self.problem.add_action(two1)

    def one1_action(self):
        got = self.problem.fluent_by_name('got')
        d = self.problem.object_by_name('d')

        one1 = unified_planning.model.action.DurativeAction('one1')
        one1.set_fixed_duration(1)

        one1.add_effect(got(d), True)
        self.problem.add_action(one1)

    def one2_action(self):
        got = self.problem.fluent_by_name('got')
        d, e = self.get_objects(['d', 'e'])

        one2 = unified_planning.model.action.DurativeAction('one2')
        one2.set_fixed_duration(1)

        one2.add_precondition(StartPreconditionTiming(), got(d), True)
        one2.add_effect(got(e), True)
        self.problem.add_action(one2)

    def two2_action(self):
        got = self.problem.fluent_by_name('got')
        c, e, f = self.get_objects(['c', 'e', 'f'])

        two2 = unified_planning.model.action.DurativeAction('two2')
        two2.set_fixed_duration(2)

        two2.add_precondition(StartPreconditionTiming(), got(c), True)
        two2.add_precondition(StartPreconditionTiming(), got(e), True)
        two2.add_effect(got(f), True)
        self.problem.add_action(two2)

    def one3_action(self):
        got = self.problem.fluent_by_name('got')
        c, e, g = self.get_objects(['c', 'e', 'g'])

        one3 = unified_planning.model.action.DurativeAction('one3')
        one3.set_fixed_duration(1)

        one3.add_precondition(StartPreconditionTiming(), got(c), True)
        one3.add_precondition(StartPreconditionTiming(), got(e), True)
        one3.add_effect(got(g), True)
        self.problem.add_action(one3)

    def one4_action(self):
        got = self.problem.fluent_by_name('got')
        g, h = self.get_objects(['g', 'h'])

        one4 = unified_planning.model.action.DurativeAction('one4')
        one4.set_fixed_duration(1)

        one4.add_precondition(StartPreconditionTiming(), got(g), True)

        one4.add_effect(got(h), True)
        self.problem.add_action(one4)

    def one5_action(self):
        got = self.problem.fluent_by_name('got')
        b, c, d, e, f, g, h, i = self.get_objects(['b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'])

        one5 = unified_planning.model.action.DurativeAction('one5')
        one5.set_fixed_duration(1)

        one5.add_precondition(StartPreconditionTiming(), got(b), True)
        one5.add_precondition(StartPreconditionTiming(), got(h), True)
        one5.add_precondition(StartPreconditionTiming(), got(f), True)

        one5.add_effect(got(i), True)

        one5.add_effect(got(b), False)
        one5.add_effect(got(c), False)
        one5.add_effect(got(d), False)
        one5.add_effect(got(e), False)
        one5.add_effect(got(f), False)
        one5.add_effect(got(g), False)
        one5.add_effect(got(h), False)
        self.problem.add_action(one5)




