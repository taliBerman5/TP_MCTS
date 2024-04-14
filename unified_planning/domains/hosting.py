import unified_planning
from unified_planning.shortcuts import *
from unified_planning.domains import Domain


class Hosting(Domain):
    def __init__(self, kind, deadline, object_amount=None, garbage_amount=None):
        Domain.__init__(self, 'hosting', kind)
        self.object_amount = object_amount
        self.garbage_amount = garbage_amount
        self.user_types()
        self.objects()
        self.fluents()
        self.actions()
        self.add_goal(deadline)

    def user_types(self):
        Broom = UserType('Broom')
        self.userTypes = dict(Broom=Broom)

    def objects(self):
        """ Init brooms """
        broom_names = ['b' + str(i) for i in range(self.object_amount)]
        brooms = [unified_planning.model.Object(b, self.userTypes['Broom']) for b in broom_names]
        self.problem.add_objects(brooms)

    def fluents(self):

        if self.garbage_amount > 1:
            lightOn = unified_planning.model.Fluent('lightOn', BoolType())
            self.problem.add_fluent(lightOn, default_initial_value=False)


        # found = unified_planning.model.Fluent('found', BoolType(), b=self.userTypes['Broom'])
        # self.problem.add_fluent(found, default_initial_value=False)

        found_broom = unified_planning.model.Fluent('found_broom', BoolType())
        if self.garbage_amount == 1:
            self.problem.add_fluent(found_broom, default_initial_value=True)
        else:
            self.problem.add_fluent(found_broom, default_initial_value=False)

        houseClean = unified_planning.model.Fluent('houseClean', BoolType())
        self.problem.add_fluent(houseClean, default_initial_value=False)

        # wet = unified_planning.model.Fluent('wet', BoolType())
        # self.problem.add_fluent(wet, default_initial_value=False)

        foodReady = unified_planning.model.Fluent('foodReady', BoolType())
        self.problem.add_fluent(foodReady, default_initial_value=False)


    def actions(self):
        if self.garbage_amount > 1:
            self.turn_on_light_action()
            self.find_broom_action()
        self.clean_action()
        self.cook_action()


    def found_prob(self):
        found = self.problem.fluent_by_name('found_broom')
        found_exp = self.problem.get_fluent_exp(found)
        def found_probability(state, actual_params):
            p = 0.7
            return {p: {found_exp: True}, 1 - p: {}}

        return found_probability

    def turn_on_light_action(self):
        lightOn = self.problem.fluent_by_name('lightOn')

        turn_on_light = unified_planning.model.DurativeAction('turn_on_light')
        turn_on_light.set_fixed_duration(8)
        # turn_on_light.add_precondition(OverallPreconditionTiming(), wet, False)

        turn_on_light.add_start_effect(lightOn, True)
        turn_on_light.add_effect(lightOn, False)
        self.problem.add_action(turn_on_light)

    def find_broom_action(self):
        lightOn, found_broom = self.get_fluents(['lightOn', 'found_broom'])

        find_broom = unified_planning.model.DurativeAction('find_broom')
        find_broom.set_fixed_duration(2)
        find_broom.add_precondition(OverallPreconditionTiming(), lightOn, True)

        find_broom.add_probabilistic_effect([found_broom],
                                              self.found_prob())
        self.problem.add_action(find_broom)



    def clean_action(self):
        """ Rest Action """
        wet, houseClean, found_broom = self.get_fluents(['wet','houseClean', 'found_broom'])

        clean = unified_planning.model.DurativeAction('clean')
        clean.set_fixed_duration(5)
        clean.add_precondition(StartPreconditionTiming(), found_broom, True)

        # clean.add_effect(wet, True)
        clean.add_effect(houseClean, True)
        self.problem.add_action(clean)

    def cook_action(self):
        houseClean, foodReady = self.get_fluents(['houseClean', 'foodReady'])

        cook = unified_planning.model.DurativeAction('cook')
        cook.set_fixed_duration(10)
        cook.add_precondition(OverallPreconditionTiming(), houseClean, False)

        cook.add_effect(foodReady, True)
        self.problem.add_action(cook)

    def add_goal(self, deadline):
        houseClean, foodReady = self.get_fluents(['houseClean', 'foodReady'])

        self.problem.add_goal(houseClean)
        self.problem.add_goal(foodReady)
        deadline_timing = Timing(delay=deadline, timepoint=Timepoint(TimepointKind.START))
        self.problem.set_deadline(deadline_timing)



# run_regular(kind='regular', deadline=10, search_time=1, search_depth=20, selection_type='avg',exploration_constant=10)

