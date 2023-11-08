import unified_planning as up
from unified_planning.domains import Domain
from unified_planning.shortcuts import *


class Strips_Prob(Domain):
    def __init__(self, kind, deadline, object_amount=None, garbage_amount=None):
        Domain.__init__(self, 'strips_prob', kind)
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
        part_names = ['a', 'b', 'c', 'd', 'e']
        parts = [unified_planning.model.Object(p, self.userTypes['Part']) for p in part_names]
        self.problem.add_objects(parts)

    def fluents(self):
        got = unified_planning.model.Fluent('got', BoolType(), p=self.userTypes['Part'])
        self.problem.add_fluent(got, default_initial_value=False)

    def add_goal(self, deadline):
        got = self.problem.fluent_by_name('got')
        a, b, c, d = self.get_objects(['a', 'b', 'c', 'd'])

        self.problem.add_goal(got(a))
        self.problem.add_goal(got(b))
        self.problem.add_goal(got(c))
        self.problem.add_goal(got(d))


        deadline_timing = Timing(delay=deadline, timepoint=Timepoint(TimepointKind.START))
        self.problem.set_deadline(deadline_timing)

    def actions(self):
        self.eight_action()
        self.four_action()
        self.two_action()
        self.one_action()
        self.garbage_actions()

    def action_prob(self, p, fluent):
        def probability(state, actual_params):
            return {p[0]: {fluent: True}, p[1]: {}}

        return probability

    def eight_action(self):
        got = self.problem.fluent_by_name('got')
        a = self.problem.object_by_name('a')

        eight = unified_planning.model.action.DurativeAction('eight')
        eight.set_fixed_duration(8)

        eight.add_effect(got(a), True)
        self.problem.add_action(eight)

    def four_action(self):
        got = self.problem.fluent_by_name('got')
        b = self.problem.object_by_name('b')

        four = unified_planning.model.action.DurativeAction('four')
        four.set_fixed_duration(4)

        four.add_probabilistic_effect([got(b)], self.action_prob(p=[0.7, 0.3], fluent=got(b)))
        self.problem.add_action(four)

    def two_action(self):
        got = self.problem.fluent_by_name('got')
        c = self.problem.object_by_name('c')

        two = unified_planning.model.action.DurativeAction('two')
        two.set_fixed_duration(2)

        two.add_probabilistic_effect([got(c)], self.action_prob(p=[0.49, 0.51], fluent=got(c)))
        self.problem.add_action(two)

    def one_action(self):
        got = self.problem.fluent_by_name('got')
        d = self.problem.object_by_name('d')

        one = unified_planning.model.action.DurativeAction('one')
        one.set_fixed_duration(1)

        one.add_probabilistic_effect([got(d)], self.action_prob(p=[0.3, 0.7], fluent=got(d)))
        self.problem.add_action(one)


    def garbage_actions(self, ):
        got = self.problem.fluent_by_name('got')
        e = self.problem.object_by_name('e')

        for i in range(self.garbage_amount):
            name = 'garbage' + str(i)
            action = unified_planning.model.action.DurativeAction(name)
            action.set_fixed_duration(1)
            action.add_effect(got(e), True)
            # action.add_probabilistic_effect([got(e)], self.action_prob(p=[0.3, 0.7], fluent=got(e)))
            self.problem.add_action(action)


