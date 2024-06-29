import unified_planning
from unified_planning.shortcuts import *
from unified_planning.domains import Domain


class Prob_MatchCellar(Domain):
    def __init__(self, kind, deadline, object_amount=None, garbage_amount=None):
        Domain.__init__(self, 'prob_match_cellar', kind)
        self.object_amount = object_amount
        self.user_types()
        self.objects()
        self.fluents()
        self.actions()
        self.add_goal(deadline)

    def user_types(self):
        Match = UserType('match')
        Fuse = UserType('fuse')
        self.userTypes = dict(Match=Match, Fuse=Fuse)

    def objects(self):
        """ Init matches """
        match_names = ['m' + str(i) for i in range(self.object_amount)]
        matches = [unified_planning.model.Object(m, self.userTypes['Match']) for m in match_names]
        self.problem.add_objects(matches)

        """ Init fuses """
        fuse_names = ['f' + str(i) for i in range(self.object_amount)]
        fuses = [unified_planning.model.Object(f, self.userTypes['Fuse']) for f in fuse_names]
        self.problem.add_objects(fuses)

    def fluents(self):
        unsued = unified_planning.model.Fluent('unused', BoolType(), m=self.userTypes['Match'])
        self.problem.add_fluent(unsued, default_initial_value=True)

        light = unified_planning.model.Fluent('light', BoolType(), m=self.userTypes['Match'])
        self.problem.add_fluent(light, default_initial_value=False)

        mended = unified_planning.model.Fluent('mended', BoolType(), f=self.userTypes['Fuse'])
        self.problem.add_fluent(mended, default_initial_value=False)

        handFree = unified_planning.model.Fluent('handFree', BoolType(), m=self.userTypes['Match'])
        self.problem.add_fluent(handFree, default_initial_value=True)

    def actions(self):
        self.light_match_action()
        self.mend_fuse_action()


    def action_prob(self, p, fluent):
        mended = self.problem.fluent_by_name("mended")
        def probability(state, actual_params):
            fluent_param = actual_params.get(fluent)
            return {p[0]: {mended(fluent_param): True}, p[1]: {}}

        return probability

    def light_match_action(self):
        """ Spraypaint Action """
        unsued, light = self.get_fluents(['unused', 'light'])

        light_match = unified_planning.model.action.DurativeAction('light_match', match=self.userTypes['Match'])
        light_match.set_fixed_duration(5)
        match = light_match.parameter('match')

        light_match.add_precondition(StartPreconditionTiming(), unsued(match), True)
        light_match.add_start_effect(unsued(match), False)
        light_match.add_start_effect(light(match), True)

        light_match.add_effect(light(match), False)

        self.problem.add_action(light_match)

    def mend_fuse_action(self):
        unsued, light, handFree, mended = self.get_fluents(['unsued', 'light', 'handFree', 'mended'])

        mend_fuse = unified_planning.model.action.DurativeAction('mend_fuse', match=self.userTypes['Match'],
                                                                 fuse=self.userTypes['Fuse'])
        mend_fuse.set_fixed_duration(2)
        match = mend_fuse.parameter('match')
        fuse = mend_fuse.parameter('fuse')

        mend_fuse.add_precondition(StartPreconditionTiming(), handFree(match), True)
        mend_fuse.add_precondition(OverallPreconditionTiming(), light(match), True)
        mend_fuse.add_start_effect(handFree(match), False)

        mend_fuse.add_probabilistic_effect([mended(fuse)], self.action_prob(p=[0.7, 0.3], fluent=fuse))
        mend_fuse.add_effect(handFree(match), True)

        self.problem.add_action(mend_fuse)

    def add_goal(self, deadline):
        mended = self.problem.fluent_by_name('mended')

        fuse_list = self.get_objects(['f' + str(i) for i in range(self.object_amount)])

        for i in range(0, self.object_amount):
            self.problem.add_goal(mended(fuse_list[i]))

        deadline_timing = Timing(delay=deadline, timepoint=Timepoint(TimepointKind.START))
        self.problem.set_deadline(deadline_timing)

# run_regular(kind='regular', deadline=10, search_time=1, search_depth=20, selection_type='avg',exploration_constant=10)
