import unified_planning
from unified_planning.shortcuts import *
from unified_planning.domains import Domain


class Stuck_Car_Robot(Domain):
    def __init__(self, kind, deadline, object_amount, garbage_amount=None):
        Domain.__init__(self, 'stuck_car', kind)
        self.object_amount = object_amount
        self.user_types()
        self.objects()
        self.fluents()
        self.actions()
        self.add_goal(deadline)

    def user_types(self):
        Robot = UserType('Robot')
        Car = UserType('Car')
        GasPedal = UserType('GasPedal')
        Rock = UserType('Rock')
        BodyPart = UserType('BodyPart')

        self.userTypes = dict(Robot=Robot, Car=Car, GasPedal=GasPedal, Rock=Rock, BodyPart=BodyPart)

    def objects(self):
        """ Init things that can be pushed """

        """ Init robot """
        robot_names = ['r' + str(i) for i in range(self.object_amount)]
        robots = [unified_planning.model.Object(r, self.userTypes['Robot']) for r in robot_names]
        self.problem.add_objects(robots)


        """ Init car """
        car_names = ['c' + str(i) for i in range(self.object_amount)]
        cars = [unified_planning.model.Object(c, self.userTypes['Car']) for c in car_names]
        self.problem.add_objects(cars)


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
        car_out = unified_planning.model.Fluent('car_out', BoolType(), c=self.userTypes['Car'])
        self.problem.add_fluent(car_out, default_initial_value=False)

        tired = unified_planning.model.Fluent('tired', BoolType(), ro=self.userTypes['Robot'])
        self.problem.add_fluent(tired, default_initial_value=False)

        got_rock = unified_planning.model.Fluent('got_rock', BoolType(), ro=self.userTypes['Robot'], r=self.userTypes['Rock'])
        self.problem.add_fluent(got_rock, default_initial_value=False)

        free = unified_planning.model.Fluent('free', BoolType(), ro=self.userTypes['Robot'], b=self.userTypes['BodyPart'])
        self.problem.add_fluent(free, default_initial_value=True)

        rock_under_car = unified_planning.model.Fluent('rock_under_car', BoolType(), c=self.userTypes['Car'], r=self.userTypes['Rock'])
        self.problem.add_fluent(rock_under_car, default_initial_value=False)

        gas_pressed = unified_planning.model.Fluent('gas_pressed', BoolType(), c=self.userTypes['Car'])
        self.problem.add_fluent(gas_pressed, default_initial_value=False)

        # To make rest action mutex with every other action in the combination setting
        dummy = unified_planning.model.Fluent('dummy', BoolType(), ro=self.userTypes['Robot'])
        self.problem.add_fluent(dummy, default_initial_value=False)

    def add_goal(self, deadline):
        car_out = self.problem.fluent_by_name('car_out')
        cars_list = self.get_objects(['c' + str(i) for i in range(self.object_amount)])

        for c in cars_list:
            self.problem.add_goal(car_out(c))

        deadline_timing = Timing(delay=deadline, timepoint=Timepoint(TimepointKind.START))
        self.problem.set_deadline(deadline_timing)

    def actions(self):
        self.rest_action()
        self.place_rock_action()
        self.search_rock_action()
        self.push_car_action()
        self.push_gas_action()
        self.push_car_gas_action()

    def tired_prob(self, robot):
        tired = self.problem.fluent_by_name('tired')
        # tired_exp = self.problem.get_fluent_exp(tired)
        #TODO: I need the line above?
        def tired_probability(state, actual_params):
            p = 0.4
            robot_param = actual_params.get(robot)
            return {p: {tired(robot_param): True}, 1 - p: {tired(robot_param): False}}

        return tired_probability


    def push_prob(self, car, probs):
        car_out, rock_under_car = self.get_fluents(['car_out', 'rock_under_car'])
        bad, good = self.get_objects(['bad', 'good'])

        # rock_0_under_exp = self.problem.get_fluent_exp(rock_under_car(bad))
        # rock_1_under_exp = self.problem.get_fluent_exp(rock_under_car(good))
        # car_out_exp = self.problem.get_fluent_exp(car_out)
        #TODO: check if the three rows above is not necessary
        def push_probability(state, actual_params):
            # The probability of getting the car out when pushing
            p = 1
            car_param = actual_params.get(car)
            predicates = state.predicates

            if car_out(car_param) not in predicates:
                # The bad rock is under the car
                if rock_under_car(car_param, bad) in predicates:
                    p = probs['bad']

                # The good rock is under the car
                elif rock_under_car(car_param, good) in predicates:
                    p = probs['good']

                # There isn't a rock under the car
                else:
                    p = probs['none']

            return {p: {car_out(car_param): True}, 1-p: {}}

        return push_probability

    def rest_action(self):
        """ Rest Action """
        tired, free = self.get_fluents(['tired', 'free'])
        hands, legs = self.get_objects(['hands', 'legs'])

        rest = unified_planning.model.DurativeAction('rest', robot=self.userTypes['Robot'])
        robot = rest.parameter('robot')
        rest.add_precondition(OverallPreconditionTiming(), free(robot, hands), True)
        rest.add_precondition(OverallPreconditionTiming(), free(robot, legs), True)
        rest.set_fixed_duration(1)
        rest.add_effect(tired(robot), False)

        self.problem.add_action(rest)

    def place_rock_action(self):
        """ Place a rock under the car Action """
        tired, free, got_rock, rock_under_car = self.get_fluents(['tired', 'free', 'got_rock', 'rock_under_car'])
        hands, legs = self.get_objects(['hands', 'legs'])


        place_rock = unified_planning.model.DurativeAction('place_rock', robot=self.userTypes['Robot'], car=self.userTypes['Car'], rock=self.userTypes['Rock'])
        robot = place_rock.parameter('robot')
        car = place_rock.parameter('car')
        rock = place_rock.parameter('rock')

        place_rock.set_fixed_duration(2)
        place_rock.add_precondition(OverallPreconditionTiming(), got_rock(robot, rock), True)
        place_rock.add_precondition(StartPreconditionTiming(), tired(robot), False)

        self.use(place_rock, free(robot, hands))
        self.use(place_rock, free(robot, legs))

        place_rock.add_effect(rock_under_car(car, rock), True)
        place_rock.add_effect(got_rock(robot, rock), False)
        place_rock.add_probabilistic_effect([tired(robot)], self.tired_prob(robot))

        self.problem.add_action(place_rock)

    def search_rock_action(self):
        """ Search a rock Action
            the robot can find a one of the rocks"""

        tired, free, got_rock = self.get_fluents(['tired', 'free', 'got_rock'])
        bad, good, hands = self.get_objects(['bad', 'good', 'hands'])

        search = unified_planning.model.action.DurativeAction('search', robot=self.userTypes['Robot'])
        robot = search.parameter('robot')
        search.set_fixed_duration(2)

        search.add_precondition(StartPreconditionTiming(), tired(robot), False)

        self.use(search, free(robot, hands))

        # import inspect as i
        # got_rock_0_exp = self.problem.get_fluent_exp(got_rock(robot, bad))
        # got_rock_1_exp = self.problem.get_fluent_exp(got_rock(robot, good))
        #TODO: check if the two rows above are needed
        def rock_probability(state, actual_params):
            # The probability of finding a good rock when searching
            p = 0.1
            robot_param = actual_params.get(robot)
            return {p: {got_rock(robot_param, bad): True, got_rock(robot_param, good): False},
                    1 - p: {got_rock(robot_param, bad): False, got_rock(robot_param, good): True}}

        search.add_probabilistic_effect([got_rock(robot, bad), got_rock(robot, good)], rock_probability)
        self.problem.add_action(search)

    def push_gas_action(self):
        """ Push Gas Pedal Action
        The probability of getting the car out is lower than push car but the robot won't get tired"""

        tired, car_out, free, = self.get_fluents(['tired', 'car_out', 'free'])
        legs = self.problem.object_by_name('legs')

        push_gas = unified_planning.model.action.DurativeAction('push_gas', robot=self.userTypes['Robot'], car=self.userTypes['Car'])
        robot = push_gas.parameter('robot')
        car = push_gas.parameter('car')
        push_gas.set_fixed_duration(2)

        push_gas.add_precondition(StartPreconditionTiming(), tired(robot), False)
        self.use(push_gas, free(robot, legs))

        push_gas.add_probabilistic_effect([car_out(car)], self.push_prob(car, probs=dict(bad=0.2, good=0.4, none=0.1)))
        self.problem.add_action(push_gas)

    def push_car_action(self):
        """ Push Car Action
            The probability of getting the car out is higher than push gas but the robot can get tired"""

        tired, car_out, free = self.get_fluents(['tired', 'car_out', 'free'])
        hands, legs = self.get_objects(['hands', 'legs'])

        push_car = unified_planning.model.action.DurativeAction('push_car', robot=self.userTypes['Robot'], car=self.userTypes['Car'])
        robot = push_car.parameter('robot')
        car = push_car.parameter('car')
        push_car.set_fixed_duration(2)

        push_car.add_precondition(StartPreconditionTiming(), tired(robot), False)
        self.use(push_car, free(robot, hands))
        # self.use(push_car, free(robot, legs))

        push_car.add_probabilistic_effect([car_out(car)], self.push_prob(car, probs=dict(bad=0.3, good=0.48, none=0.1)))
        push_car.add_probabilistic_effect([tired(robot)], self.tired_prob(robot))
        self.problem.add_action(push_car)


    def push_car_gas_action(self):
        tired, car_out, free = self.get_fluents(['tired', 'car_out', 'free'])
        hands, legs = self.get_objects(['hands', 'legs'])

        push_car_gas = unified_planning.model.action.DurativeAction('push_car_gas', robot=self.userTypes['Robot'], car=self.userTypes['Car'])
        robot = push_car_gas.parameter('robot')
        car = push_car_gas.parameter('car')
        push_car_gas.set_fixed_duration(4)

        push_car_gas.add_precondition(StartPreconditionTiming(), tired(robot), False)
        self.use(push_car_gas, free(robot, hands))
        self.use(push_car_gas, free(robot, legs))

        push_car_gas.add_probabilistic_effect([car_out(car)], self.push_prob(car, probs=dict(bad=0.4, good=0.9, none=0.2)))
        push_car_gas.add_probabilistic_effect([tired(robot)], self.tired_prob(robot))

        self.problem.add_action(push_car_gas)


    # def remove_actions(self, converted_problem):
    #     #TODO: needs to update this. rest(car) action cant be preformed with other actions of the same car
    #     for action in converted_problem.actions[:]:
    #         if isinstance(action, CombinationAction):
    #             if 'rest' in action.name:
    #                 converted_problem.actions.remove(action)


# run_regular(kind='regular', deadline=10, search_time=1, search_depth=20, selection_type='avg',exploration_constant=10)

