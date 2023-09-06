import unified_planning
from unified_planning.shortcuts import *


class Nasa_Rover:
    def __init__(self, kind, deadline):
        self.problem = unified_planning.model.Problem('nasa_rover')
        self.kind = kind
        self.user_types()
        self.objects()
        self.fluents()
        self.actions()
        self.add_goal(deadline)
        self.set_initial_state()

    def get_fluents(self, string):
        return [self.problem.fluent_by_name(s) for s in string]

    def get_objects(self, string):
        return [self.problem.object_by_name(s) for s in string]

    def user_types(self):
        Rover = UserType('Rover')
        Store = UserType('Store')
        Camera = UserType('Camera')
        Objective = UserType('Objective')
        Rock = UserType('Rock')
        Hand = UserType('Hand')

        self.userTypes = dict(Rover=Rover, Store=Store, Camera=Camera, Objective=Objective, Rock=Rock, Hand=Hand)

    def objects(self):
        """ Init rover """
        rover_names = ['r1']
        rovers = [unified_planning.model.Object(r, self.userTypes['Rover']) for r in rover_names]
        self.problem.add_objects(rovers)

        """ Init store """
        store_names = ['s1', 's2']
        stores = [unified_planning.model.Object(s, self.userTypes['Store']) for s in store_names]
        self.problem.add_objects(stores)

        """ Init camera """
        camera_names = ['c1']
        cameras = [unified_planning.model.Object(c, self.userTypes['Camera']) for c in camera_names]
        self.problem.add_objects(cameras)

        """ Init objective """
        objective_names = ['o1']
        objectives = [unified_planning.model.Object(o, self.userTypes['Objective']) for o in objective_names]
        self.problem.add_objects(objectives)

        """ Init Rock """
        rock_names = ['x1', 'x2']
        rocks = [unified_planning.model.Object(r, self.userTypes['Rock']) for r in rock_names]
        self.problem.add_objects(rocks)

        """ Init Hand """
        hand_names = ['h1', 'h2']
        hands = [unified_planning.model.Object(h, self.userTypes['Hand']) for h in hand_names]
        self.problem.add_objects(hands)

    def fluents(self):
        have_rock_analysis = unified_planning.model.Fluent('have_rock_analysis', BoolType(),
                                                           rover=self.userTypes['Rover'], rock=self.userTypes['Rock'])
        self.problem.add_fluent(have_rock_analysis, default_initial_value=False)

        communicated_rock_data = unified_planning.model.Fluent('communicated_rock_data', BoolType(),
                                                               rock=self.userTypes['Rock'])
        self.problem.add_fluent(communicated_rock_data, default_initial_value=False)

        full = unified_planning.model.Fluent('full', BoolType(), store=self.userTypes['Store'])
        self.problem.add_fluent(full, default_initial_value=False)

        ready_to_drop = unified_planning.model.Fluent('ready_to_drop', BoolType(), store=self.userTypes['Store'])
        self.problem.add_fluent(ready_to_drop, default_initial_value=False)

        calibrated = unified_planning.model.Fluent('calibrated', BoolType(), camera=self.userTypes['Camera'],
                                                   objective=self.userTypes['Objective'])
        self.problem.add_fluent(calibrated, default_initial_value=False)

        have_image = unified_planning.model.Fluent('have_image', BoolType(), rRover=self.userTypes['Rover'],
                                                   objective=self.userTypes['Objective'])
        self.problem.add_fluent(have_image, default_initial_value=False)

        communicated_image_data = unified_planning.model.Fluent('communicated_image_data', BoolType(),
                                                                objective=self.userTypes['Objective'])
        self.problem.add_fluent(communicated_image_data, default_initial_value=False)

        store_of = unified_planning.model.Fluent('store_of', BoolType(), store=self.userTypes['Store'],
                                                 rover=self.userTypes['Rover'])
        self.problem.add_fluent(store_of, default_initial_value=False)

        on_board = unified_planning.model.Fluent('on_board', BoolType(), camera=self.userTypes['Camera'],
                                                 rover=self.userTypes['Rover'])
        self.problem.add_fluent(on_board, default_initial_value=False)

        free_h = unified_planning.model.Fluent('free_h', BoolType(), hand=self.userTypes['Hand'])
        self.problem.add_fluent(free_h, default_initial_value=False)

        free_c = unified_planning.model.Fluent('free_c', BoolType(), camera=self.userTypes['Camera'])
        self.problem.add_fluent(free_c, default_initial_value=False)

        free_s = unified_planning.model.Fluent('free_s', BoolType(), store=self.userTypes['Store'])
        self.problem.add_fluent(free_s, default_initial_value=True)

        good = unified_planning.model.Fluent('good', BoolType(), hand=self.userTypes['Hand'])
        self.problem.add_fluent(good, default_initial_value=False)

        hand_of = unified_planning.model.Fluent('hand_of', BoolType(), hand=self.userTypes['Hand'],
                                                rover=self.userTypes['Rover'])
        self.problem.add_fluent(hand_of, default_initial_value=False)

        ready = unified_planning.model.Fluent('ready', BoolType(), hand=self.userTypes['Hand'],
                                              rock=self.userTypes['Rock'])
        self.problem.add_fluent(ready, default_initial_value=False)

    def set_initial_state(self):
        store_of, on_board, free_h, free_c, good, hand_of = self.get_fluents(
            ['store_of', 'on_board', 'free_h', 'free_c', 'good', 'hand_of'])
        s1, s2, r1, c1, h1, h2 = self.get_objects(['s1', 's2', 'r1', 'c1', 'h1', 'h2'])

        self.problem.set_initial_value(store_of(s1, r1), True)
        self.problem.set_initial_value(store_of(s2, r1), True)
        self.problem.set_initial_value(on_board(c1, r1), True)
        self.problem.set_initial_value(free_h(h1), True)
        self.problem.set_initial_value(free_h(h2), True)
        self.problem.set_initial_value(free_c(c1), True)
        self.problem.set_initial_value(good(h1), True)
        self.problem.set_initial_value(hand_of(h1, r1), True)
        self.problem.set_initial_value(hand_of(h2, r1), True)

    def add_goal(self, deadline):
        communicated_rock_data, communicated_image_data = self.get_fluents(
            ['communicated_rock_data', 'communicated_image_data'])
        x1, x2, o1 = self.get_objects(['x1', 'x2', 'o1'])
        self.problem.add_goal(communicated_rock_data(x1))
        self.problem.add_goal(communicated_rock_data(x2))
        self.problem.add_goal(communicated_image_data(o1))

        deadline_timing = Timing(delay=deadline, timepoint=Timepoint(TimepointKind.START))
        self.problem.set_deadline(deadline_timing)

    def actions(self):
        self.sample_rock_good_action()
        self.sample_rock_action()
        self.drop_action()
        self.calibrate_action()
        self.turn_on_dropping_action()
        self.turn_on_good_hand()
        self.turn_on_hand()
        self.take_image_action()
        self.communicate_rock_data_action()
        self.communicate_image_data_action()

    def sample_prob(self, hand, rock, store, rover, p):
        full, have_rock_analysis, free_h, ready = self.get_fluents(['full', 'have_rock_analysis', 'free_h', 'ready'])

        def sample_probability(state, actual_params):
            hand_param = actual_params.get(hand)
            rock_param = actual_params.get(rock)
            store_param = actual_params.get(store)
            rover_param = actual_params.get(rover)
            return {p[0]: {full(store_param): True, have_rock_analysis(rover_param, rock_param): True,
                           free_h(hand_param): True,
                           ready(hand_param, rock_param): False},
                    p[1]: {ready(hand_param, rock_param): False, free_h(hand_param): True}, p[2]: {}}

        return sample_probability

    def turn_hand_prob(self, hand, rock):
        free_h, ready = self.get_fluents(['free_h', 'ready'])

        def turn_on_hand_probability(state, actual_params):
            hand_param = actual_params.get(hand)
            rock_param = actual_params.get(rock)

            return {0.8: {free_h(hand_param): False, ready(hand_param, rock_param): True}, 0.2: {}}

        return turn_on_hand_probability

    def take_image_prob(self, rover, objective, camera):
        have_image, calibrated = self.get_fluents(['have_image', 'calibrated'])

        def take_image_probability(state, actual_params):
            rover_param = actual_params.get(rover)
            objective_param = actual_params.get(objective)
            camera_param = actual_params.get(camera)

            return {
                0.9: {have_image(rover_param, objective_param): True, calibrated(camera_param, objective_param): False},
                0.1: {have_image(rover_param, objective_param): False,
                      calibrated(camera_param, objective_param): False}}

        return take_image_probability

    def communicate_prob(self, p, fluent, param):
        def communicate_probability(state, actual_params):
            actual_param = actual_params.get(param)

            return {p[0]: {fluent(actual_param): True},
                    p[1]: {fluent(actual_param): False}}

        return communicate_probability

    def sample_rock_good_action(self):
        """ sample_rock_good Action """
        store_of, full, ready_to_drop, ready, hand_of, good, free_s, have_rock_analysis, free_h = self.get_fluents(
            ['store_of', 'full', 'ready_to_drop', 'ready', 'hand_of', 'good', 'free_s', 'have_rock_analysis', 'free_h']
        )

        sample_rock_good = unified_planning.model.action.DurativeAction('sample_rock_good',
                                                                        rover=self.userTypes['Rover'],
                                                                        store=self.userTypes['Store'],
                                                                        rock=self.userTypes['Rock'],
                                                                        hand=self.userTypes['Hand'])
        sample_rock_good.set_fixed_duration(5)
        rover = sample_rock_good.parameter('rover')
        store = sample_rock_good.parameter('store')
        rock = sample_rock_good.parameter('rock')
        hand = sample_rock_good.parameter('hand')
        sample_rock_good.add_precondition(OverallPreconditionTiming(), store_of(store, rover), True)
        sample_rock_good.add_precondition(OverallPreconditionTiming(), full(store), False)
        sample_rock_good.add_precondition(OverallPreconditionTiming(), ready_to_drop(store), False)
        sample_rock_good.add_precondition(OverallPreconditionTiming(), ready(hand, rock), True)
        sample_rock_good.add_precondition(OverallPreconditionTiming(), hand_of(hand, rover), True)
        sample_rock_good.add_precondition(OverallPreconditionTiming(), good(hand), True)

        if self.kind in ['regular', 'regular_as_baseline']:
            self.use(sample_rock_good, free_s(store))

        sample_rock_good.add_probabilistic_effect(
            [full(store), have_rock_analysis(rover, rock), free_h(hand), ready(hand, rock)],
            self.sample_prob(hand, rock, store, rover, p=[0.9, 0.051, 0.049]))
        self.problem.add_action(sample_rock_good)

    def sample_rock_action(self):
        """ sample_rock Action """
        store_of, full, ready_to_drop, ready, hand_of, good, free_s, have_rock_analysis, free_h = self.get_fluents(
            ['store_of', 'full', 'ready_to_drop', 'ready', 'hand_of', 'good', 'free_s', 'have_rock_analysis', 'free_h']
        )

        sample_rock = unified_planning.model.action.DurativeAction('sample_rock',
                                                                   rover=self.userTypes['Rover'],
                                                                   store=self.userTypes['Store'],
                                                                   rock=self.userTypes['Rock'],
                                                                   hand=self.userTypes['Hand'])
        sample_rock.set_fixed_duration(10)
        rover = sample_rock.parameter('rover')
        store = sample_rock.parameter('store')
        rock = sample_rock.parameter('rock')
        hand = sample_rock.parameter('hand')
        sample_rock.add_precondition(OverallPreconditionTiming(), store_of(store, rover), True)
        sample_rock.add_precondition(OverallPreconditionTiming(), full(store), False)
        sample_rock.add_precondition(OverallPreconditionTiming(), ready_to_drop(store), False)
        sample_rock.add_precondition(OverallPreconditionTiming(), ready(hand, rock), True)
        sample_rock.add_precondition(OverallPreconditionTiming(), hand_of(hand, rover), True)
        sample_rock.add_precondition(OverallPreconditionTiming(), good(hand), False)

        if self.kind in ['regular', 'regular_as_baseline']:
            self.use(sample_rock, free_s(store))

        sample_rock.add_probabilistic_effect(
            [full(store), have_rock_analysis(rover, rock), free_h(hand), ready(hand, rock)],
            self.sample_prob(hand, rock, store, rover, p=[0.7, 0.05, 0.25]))
        self.problem.add_action(sample_rock)

    def drop_action(self):
        """ drop Action """
        ready_to_drop, full = self.get_fluents(['ready_to_drop', 'full'])

        drop = unified_planning.model.action.DurativeAction('drop', store=self.userTypes['Store'])
        drop.set_fixed_duration(3)
        store = drop.parameter('store')
        drop.add_precondition(OverallPreconditionTiming(), ready_to_drop(store), True)
        drop.add_effect(full(store), False)
        drop.add_effect(ready_to_drop(store), False)
        self.problem.add_action(drop)

    def calibrate_action(self):
        """ calibrate Action """
        calibrated = self.problem.fluent_by_name('calibrated')

        calibrate = unified_planning.model.action.DurativeAction('calibrate',
                                                                 camera=self.userTypes['Camera'],
                                                                 objective=self.userTypes['Objective'])
        calibrate.set_fixed_duration(4)
        camera = calibrate.parameter('camera')
        objective = calibrate.parameter('objective')
        calibrate.add_effect(calibrated(camera, objective), True)
        self.problem.add_action(calibrate)

    def turn_on_dropping_action(self):
        """ turn_on_dropping Action """
        ready_to_drop, free_s = self.get_fluents(['ready_to_drop', 'free_s'])

        turn_on_dropping = unified_planning.model.action.DurativeAction('turn_on_dropping',
                                                                        store=self.userTypes['Store'])
        turn_on_dropping.set_fixed_duration(1)
        store = turn_on_dropping.parameter('store')

        if self.kind == 'regular_as_baseline':
            self.use(turn_on_dropping, free_s(store))

        turn_on_dropping.add_effect(ready_to_drop(store), True)
        self.problem.add_action(turn_on_dropping)

    def turn_on_good_hand(self):
        """ turn_on_good_hand Action """
        free_h, good, ready = self.get_fluents(['free_h', 'good', 'ready'])

        turn_on_good_hand = unified_planning.model.action.DurativeAction('turn_on_good_hand',
                                                                         hand=self.userTypes['Hand'],
                                                                         rock=self.userTypes['Rock'])
        turn_on_good_hand.set_fixed_duration(1)
        hand = turn_on_good_hand.parameter('hand')
        rock = turn_on_good_hand.parameter('rock')
        turn_on_good_hand.add_precondition(OverallPreconditionTiming(), good(hand), True)

        if self.kind in ['regular', 'regular_as_baseline']:
            turn_on_good_hand.add_precondition(StartPreconditionTiming(), free_h(hand), True)
            turn_on_good_hand.add_start_effect(free_h(hand), False)

        if self.kind == 'combination':
            turn_on_good_hand.add_precondition(OverallPreconditionTiming(), free_h(hand), True)
            turn_on_good_hand.add_effect(free_h(hand), False)

        turn_on_good_hand.add_effect(ready(hand, rock), True)
        self.problem.add_action(turn_on_good_hand)

    def turn_on_hand(self):
        """ turn_on_hand Action """
        free_h, good, ready = self.get_fluents(['free_h', 'good', 'ready'])
        turn_on_hand = unified_planning.model.action.InstantaneousAction('turn_on_hand',
                                                                         hand=self.userTypes['Hand'],
                                                                         rock=self.userTypes['Rock'])
        hand = turn_on_hand.parameter('hand')
        rock = turn_on_hand.parameter('rock')
        turn_on_hand.add_precondition(free_h(hand), True)
        turn_on_hand.add_precondition(good(hand), False)

        turn_on_hand.add_probabilistic_effect([free_h(hand), ready(hand, rock)], self.turn_hand_prob(hand, rock))
        self.problem.add_action(turn_on_hand)

    def take_image_action(self):
        """ take_image Action """
        calibrated, on_board, have_image = self.get_fluents(['calibrated', 'on_board', 'have_image'])

        take_image = unified_planning.model.action.DurativeAction('take_image',
                                                                  rover=self.userTypes['Rover'],
                                                                  objective=self.userTypes['Objective'],
                                                                  camera=self.userTypes['Camera'])
        take_image.set_fixed_duration(6)
        rover = take_image.parameter('rover')
        objective = take_image.parameter('objective')
        camera = take_image.parameter('camera')
        take_image.add_precondition(OverallPreconditionTiming(), calibrated(camera, objective), True)
        take_image.add_precondition(OverallPreconditionTiming(), on_board(camera, rover), True)

        take_image.add_probabilistic_effect([have_image(rover, objective), calibrated(camera, objective)],
                                            self.take_image_prob(rover, objective, camera))
        self.problem.add_action(take_image)

    def communicate_rock_data_action(self):
        """ communicate_rock_data Action """
        have_rock_analysis, communicated_rock_data = self.get_fluents(['have_rock_analysis', 'communicated_rock_data'])
        communicate_rock_data = unified_planning.model.action.DurativeAction('communicate_rock_data',
                                                                             rover=self.userTypes['Rover'],
                                                                             rock=self.userTypes['Rock'])
        communicate_rock_data.set_fixed_duration(2)
        rover = communicate_rock_data.parameter('rover')
        rock = communicate_rock_data.parameter('rock')
        communicate_rock_data.add_precondition(OverallPreconditionTiming(), have_rock_analysis(rover, rock), True)

        communicate_rock_data.add_probabilistic_effect([communicated_rock_data(rock)],
                                                       self.communicate_prob(p=[0.6, 0.4],
                                                                             fluent=communicated_rock_data, param=rock))
        self.problem.add_action(communicate_rock_data)

    def communicate_image_data_action(self):
        """ communicate_image_data Action """
        have_image, communicated_image_data = self.get_fluents(['have_image', 'communicated_image_data'])

        communicate_image_data = unified_planning.model.action.DurativeAction('communicate_image_data',
                                                                              rover=self.userTypes['Rover'],
                                                                              objective=self.userTypes['Objective'])
        communicate_image_data.set_fixed_duration(2)
        rover = communicate_image_data.parameter('rover')
        objective = communicate_image_data.parameter('objective')
        communicate_image_data.add_precondition(OverallPreconditionTiming(), have_image(rover, objective), True)

        communicate_image_data.add_probabilistic_effect([communicated_image_data(objective)],
                                                        self.communicate_prob(p=[0.6, 0.4],
                                                                              fluent=communicated_image_data,
                                                                              param=objective))
        self.problem.add_action(communicate_image_data)

    def use(self, action, fluent):
        action.add_precondition(StartPreconditionTiming(), fluent, True)
        action.add_start_effect(fluent, False)
        action.add_effect(fluent, True)


def run_regular(kind):
    nasa_rover = Nasa_Rover(kind=kind, deadline=20)
    grounder = unified_planning.engines.compilers.Grounder()
    grounding_result = grounder._compile(nasa_rover.problem)
    ground_problem = grounding_result.problem

    convert_problem = unified_planning.engines.Convert_problem(ground_problem)
    converted_problem = convert_problem._converted_problem
    mdp = unified_planning.engines.MDP(converted_problem, discount_factor=0.95)
    up.engines.solvers.mcts.plan(mdp, steps=90, search_depth=40, exploration_constant=50, search_time=20)


def run_combination():
    nasa_rover = Nasa_Rover(kind='combination', deadline=27)
    grounder = unified_planning.engines.compilers.Grounder()
    grounding_result = grounder._compile(nasa_rover.problem)
    ground_problem = grounding_result.problem

    convert_combination_problem = unified_planning.engines.Convert_problem_combination(ground_problem)
    converted_problem = convert_combination_problem._converted_problem

    mdp = unified_planning.engines.combinationMDP(converted_problem, discount_factor=0.95)
    split_mdp = unified_planning.engines.MDP(convert_combination_problem._split_problem, discount_factor=0.95)

    up.engines.solvers.rtdp.plan(mdp, split_mdp, steps=90, search_depth=40, search_time=60)


# run_regular(kind='regular')
# run_regular(kind='regular_as_baseline')
run_combination()
