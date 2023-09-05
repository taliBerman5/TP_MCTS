import unified_planning
from unified_planning.shortcuts import *


class Stuck_Car:
    def __init__(self):
        self.problem = unified_planning.model.Problem('stuck_car')
        self.user_types()
        self.objects()
        self.fluents()
        self.actions()
        self.add_goal()

    def user_types(self):
        Car = UserType('Car')
        GasPedal = UserType('GasPedal')
        Rock = UserType('Rock')
        BodyPart = UserType('BodyPart')

        self.userTypes = dict(Car=Car, GasPedal=GasPedal, Rock=Rock, BodyPart=BodyPart)

    def objects(self):
        """ Init things that can be pushed """
        car = unified_planning.model.Object('car', self.userTypes['Car'])
        self.problem.add_object(car)

        gasPedal = unified_planning.model.Object('gasPedal', self.userTypes['GasPedal'])
        self.problem.add_object(gasPedal)

        """ Init rocks """
        rocks_names = ['bad', 'good']
        rocks = [unified_planning.model.Object(r, self.userTypes['Rock']) for r in rocks_names]
        self.problem.add_objects(rocks)

        """ Init body parts -
            when performing an action at least one of the body parts will be occupied
        """
        bodyParts_names = ['hands', 'legs']
        bodyParts = [unified_planning.model.Object(b, self.userTypes['BodyPart']) for b in bodyParts_names]
        self.problem.add_objects(bodyParts)

    def fluents(self):
        car_out = unified_planning.model.Fluent('car_out', BoolType())
        self.problem.add_fluent(car_out, default_initial_value=False)

        tired = unified_planning.model.Fluent('tired', BoolType())
        self.problem.add_fluent(tired, default_initial_value=False)

        got_rock = unified_planning.model.Fluent('got_rock', BoolType(), r=self.userTypes['Rock'])
        self.problem.add_fluent(got_rock, default_initial_value=False)

        free = unified_planning.model.Fluent('free', BoolType(), b=self.userTypes['BodyPart'])
        self.problem.add_fluent(free, default_initial_value=True)

        rock_under_car = unified_planning.model.Fluent('rock_under_car', BoolType(), r=self.userTypes['Rock'])
        self.problem.add_fluent(rock_under_car, default_initial_value=False)

        gas_pressed = unified_planning.model.Fluent('gas_pressed', BoolType())
        self.problem.add_fluent(gas_pressed, default_initial_value=False)

    def actions(self):
        self.tired_prob()

        self.rest_action()
        self.place_rock_action()
        self.search_rock_action()
        self.push_car_actions()
        self.push_gas_actions()

    def tired_prob(self):
        tired = self.problem.fluent_by_name('tired')
        tired_exp = self.problem.get_fluent_exp(tired)

        def tired_probability(state, actual_params):
            p = 0.4
            return {p: {tired_exp: True}, 1 - p: {tired_exp: False}}

        return tired_probability

    def push_car_prob(self, probs):
        car_out = self.problem.fluent_by_name('car_out')
        rock_under_car = self.problem.fluent_by_name('rock_under_car')
        bad = self.problem.object_by_name('bad')
        good = self.problem.object_by_name('good')

        rock_0_under_exp = self.problem.get_fluent_exp(rock_under_car(bad))
        rock_1_under_exp = self.problem.get_fluent_exp(rock_under_car(good))
        car_out_exp = self.problem.get_fluent_exp(car_out)

        def push_car_probability(state, actual_params):
            # The probability of getting the car out when pushing the car
            p = 1
            predicates = state.predicates

            if car_out_exp not in predicates:
                # The bad rock is under the car
                if rock_0_under_exp in predicates:
                    p = probs['bad']

                # The good rock is under the car
                elif rock_1_under_exp in predicates:
                    p = probs['good']

                # There isn't a rock under the car
                else:
                    p = probs['none']

            return {p: {car_out_exp: True}, 1-p: {}}

        return push_car_probability

    def rest_action(self):
        """ Rest Action """
        tired = self.problem.fluent_by_name('tired')
        free = self.problem.fluent_by_name('free')
        hands = self.problem.object_by_name('hands')
        legs = self.problem.object_by_name('legs')

        rest = unified_planning.model.DurativeAction('rest')
        rest.add_precondition(OverallPreconditionTiming(), free(hands), True)
        rest.add_precondition(OverallPreconditionTiming(), free(legs), True)
        rest.set_fixed_duration(1)
        rest.add_effect(tired, False)
        self.problem.add_action(rest)

    def place_rock_action(self):
        """ Place a rock under the car Action """
        tired = self.problem.fluent_by_name('tired')
        free = self.problem.fluent_by_name('free')
        got_rock = self.problem.fluent_by_name('got_rock')
        rock_under_car = self.problem.fluent_by_name('rock_under_car')
        hands = self.problem.object_by_name('hands')
        legs = self.problem.object_by_name('legs')

        place_rock = unified_planning.model.DurativeAction('place_rock', rock=self.userTypes['Rock'])
        rock = place_rock.parameter('rock')
        place_rock.set_fixed_duration(2)
        place_rock.add_precondition(OverallPreconditionTiming(), got_rock(rock), True)
        place_rock.add_precondition(StartPreconditionTiming(), tired, False)

        self.use(place_rock, free(hands))
        self.use(place_rock, free(legs))

        place_rock.add_effect(rock_under_car(rock), True)
        place_rock.add_effect(got_rock(rock), False)
        place_rock.add_probabilistic_effect([tired], self.tired_prob())
        self.problem.add_action(place_rock)

    def search_rock_action(self):
        """ Search a rock Action
            the robot can find a one of the rocks"""

        tired = self.problem.fluent_by_name('tired')
        free = self.problem.fluent_by_name('free')
        got_rock = self.problem.fluent_by_name('got_rock')
        bad = self.problem.object_by_name('bad')
        good = self.problem.object_by_name('good')
        hands = self.problem.object_by_name('hands')
        legs = self.problem.object_by_name('legs')

        search = unified_planning.model.action.DurativeAction('search')
        search.set_fixed_duration(2)

        search.add_precondition(StartPreconditionTiming(), tired, False)

        self.use(search, free(hands))
        self.use(search, free(legs))

        # import inspect as i
        got_rock_0_exp = self.problem.get_fluent_exp(got_rock(bad))
        got_rock_1_exp = self.problem.get_fluent_exp(got_rock(good))

        def rock_probability(state, actual_params):
            # The probability of finding a good rock when searching
            p = 0.1
            return {p: {got_rock_0_exp: True, got_rock_1_exp: False},
                    1 - p: {got_rock_0_exp: False, got_rock_1_exp: True}}

        search.add_probabilistic_effect([got_rock(bad), got_rock(good)], rock_probability)
        self.problem.add_action(search)

    def push_gas_actions(self):
        """ Push Gas Pedal Action """

        tired = self.problem.fluent_by_name('tired')
        rock_under_car = self.problem.fluent_by_name('rock_under_car')
        car_out = self.problem.fluent_by_name('car_out')
        free = self.problem.fluent_by_name('free')
        bad = self.problem.object_by_name('bad')
        good = self.problem.object_by_name('good')
        legs = self.problem.object_by_name('legs')

        gas_pressed = self.problem.fluent_by_name('gas_pressed')

        # Push gas action simultaneously with Push car action
        push_gas_simultaneously = unified_planning.model.action.DurativeAction('push_gas_simultaneously')
        push_gas_simultaneously.set_fixed_duration(2)

        push_gas_simultaneously.add_precondition(StartPreconditionTiming(), tired, False)
        self.use(push_gas_simultaneously, free(legs))
        push_gas_simultaneously.add_start_effect(gas_pressed, True)
        push_gas_simultaneously.add_effect(gas_pressed, False)
        self.problem.add_action(push_gas_simultaneously)

        # Push gas action unable to run simultaneously with Push car action
        push_gas = unified_planning.model.action.DurativeAction('push_gas')
        push_gas.set_fixed_duration(2)

        push_gas.add_precondition(StartPreconditionTiming(), tired, False)
        self.use(push_gas, free(legs))

        rock_0_under_exp = self.problem.get_fluent_exp(rock_under_car(bad))
        rock_1_under_exp = self.problem.get_fluent_exp(rock_under_car(good))
        car_out_exp = self.problem.get_fluent_exp(car_out)

        def push_gas_probability(state, actual_params):
            # The probability of getting the car out when pushing the gas padel
            p = 1
            predicates = state.predicates

            if car_out_exp not in predicates:
                # The bad rock is under the car
                if rock_0_under_exp in predicates:
                    p = 0.2

                # The good rock is under the car
                elif rock_1_under_exp in predicates:
                    p = 0.45

                # There isn't a rock under the car
                else:
                    p = 0.1

            return {p: {car_out_exp: True}, 1 - p: {}}

        push_gas.add_probabilistic_effect([car_out], push_gas_probability)
        push_gas.add_probabilistic_effect([tired], self.tired_prob())

        self.problem.add_action(push_gas)

    def push_car_actions(self):
        """ Push Car Action """

        tired = self.problem.fluent_by_name('tired')
        car_out = self.problem.fluent_by_name('car_out')
        free = self.problem.fluent_by_name('free')
        hands = self.problem.object_by_name('hands')

        gas_pressed = self.problem.fluent_by_name('gas_pressed')

        # Push car action simultaneously with Push gas action
        push_car_simultaneously = unified_planning.model.action.DurativeAction('push_car_simultaneously')
        push_car_simultaneously.set_fixed_duration(2)

        push_car_simultaneously.add_precondition(StartPreconditionTiming(), tired, False)
        push_car_simultaneously.add_precondition(OverallPreconditionTiming(), gas_pressed, True)
        self.use(push_car_simultaneously, free(hands))

        push_car_simultaneously.add_probabilistic_effect([car_out], self.push_car_prob(probs=dict(bad=0.4, good=0.95, none=0.2)))
        push_car_simultaneously.add_probabilistic_effect([tired], self.tired_prob())
        self.problem.add_action(push_car_simultaneously)

        # Push car action unable to run simultaneously with Push gas action
        push_car = unified_planning.model.action.DurativeAction('push_car')
        push_car.set_fixed_duration(2)

        push_car.add_precondition(StartPreconditionTiming(), tired, False)
        self.use(push_car, free(hands))

        push_car.add_probabilistic_effect([car_out], self.push_car_prob(probs=dict(bad=0.2, good=0.4, none=0.1)))
        push_car.add_probabilistic_effect([tired], self.tired_prob())

        self.problem.add_action(push_car)

    def add_goal(self):
        car_out = self.problem.fluent_by_name('car_out')

        self.problem.add_goal(car_out)
        deadline = Timing(delay=10, timepoint=Timepoint(TimepointKind.START))
        self.problem.set_deadline(deadline)

    def use(self, action, fluent):
        action.add_precondition(StartPreconditionTiming(), fluent, True)
        action.add_start_effect(fluent, False)
        action.add_effect(fluent, True)


stuck_car = Stuck_Car()

grounder = unified_planning.engines.compilers.Grounder()
grounding_result = grounder._compile(stuck_car.problem)
ground_problem = grounding_result.problem

# convert_combination_problem = unified_planning.engines.Convert_problem_combination(ground_problem)
# converted_problem = convert_combination_problem._converted_problem
# mdp = unified_planning.engines.combinationMDP(converted_problem, discount_factor=0.95)
# split_mdp = unified_planning.engines.MDP(convert_combination_problem._split_problem, discount_factor=0.95)
# up.engines.solvers.rtdp.plan(mdp, split_mdp, steps=90, search_depth=40)

convert_problem = unified_planning.engines.Convert_problem(ground_problem)
# print(convert_problem)
converted_problem = convert_problem._converted_problem
mdp = unified_planning.engines.MDP(converted_problem, discount_factor=0.95)

up.engines.solvers.mcts.plan(mdp, steps=10, search_depth=20, exploration_constant=10)
