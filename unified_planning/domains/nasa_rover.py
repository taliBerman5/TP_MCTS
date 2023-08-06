import unified_planning
from unified_planning.shortcuts import *

problem = unified_planning.model.Problem('nasa_rover')

""" Init rover """
Rover = UserType('Rover')
rover_names = ['r1']
rovers = [unified_planning.model.Object(r, Rover) for r in rover_names]
problem.add_objects(rovers)

""" Init store """
Store = UserType('Store')
store_names = ['s1', 's2']
stores = [unified_planning.model.Object(s, Store) for s in store_names]
problem.add_objects(stores)

""" Init camera """
Camera = UserType('Camera')
camera_names = ['c1']
cameras = [unified_planning.model.Object(c, Camera) for c in camera_names]
problem.add_objects(cameras)

""" Init objective """
Objective = UserType('Objective')
objective_names = ['o1']
objectives = [unified_planning.model.Object(o, Objective) for o in objective_names]
problem.add_objects(objectives)

""" Init Rock """
Rock = UserType('Rock')
rock_names = ['x1', 'x2']
rocks = [unified_planning.model.Object(r, Rock) for r in rock_names]
problem.add_objects(rocks)

""" Init Hand """
Hand = UserType('Hand')
hand_names = ['h1', 'h2']
hands = [unified_planning.model.Object(h, Hand) for h in hand_names]
problem.add_objects(hands)

# Predicates
have_rock_analysis = unified_planning.model.Fluent('have_rock_analysis', BoolType(), rover=Rover, rock=Rock)
problem.add_fluent(have_rock_analysis, default_initial_value=False)

communicated_rock_data = unified_planning.model.Fluent('communicated_rock_data', BoolType(), rock=Rock)
problem.add_fluent(communicated_rock_data, default_initial_value=False)

full = unified_planning.model.Fluent('full', BoolType(), store=Store)
problem.add_fluent(full, default_initial_value=False)

ready_to_drop = unified_planning.model.Fluent('ready_to_drop', BoolType(), store=Store)
problem.add_fluent(ready_to_drop, default_initial_value=False)

calibrated = unified_planning.model.Fluent('calibrated', BoolType(), camera=Camera, objective=Objective)
problem.add_fluent(calibrated, default_initial_value=False)

have_image = unified_planning.model.Fluent('have_image', BoolType(), rRover=Rover, objective=Objective)
problem.add_fluent(have_image, default_initial_value=False)

communicated_image_data = unified_planning.model.Fluent('communicated_image_data', BoolType(), objective=Objective)
problem.add_fluent(communicated_image_data, default_initial_value=False)

store_of = unified_planning.model.Fluent('store_of', BoolType(), store=Store, rover=Rover)
problem.add_fluent(store_of, default_initial_value=False)

on_board = unified_planning.model.Fluent('on_board', BoolType(), camera=Camera, rover=Rover)
problem.add_fluent(on_board, default_initial_value=False)

free_h = unified_planning.model.Fluent('free_h', BoolType(), hand=Hand)
problem.add_fluent(free_h, default_initial_value=False)

free_c = unified_planning.model.Fluent('free_c', BoolType(), camera=Camera)
problem.add_fluent(free_c, default_initial_value=False)

good = unified_planning.model.Fluent('good', BoolType(), hand=Hand)
problem.add_fluent(good, default_initial_value=False)

hand_of = unified_planning.model.Fluent('hand_of', BoolType(), hand=Hand, rover=Rover)
problem.add_fluent(hand_of, default_initial_value=False)

ready = unified_planning.model.Fluent('ready', BoolType(), hand=Hand, rock=Rock)
problem.add_fluent(ready, default_initial_value=False)

problem.set_initial_value(store_of(stores[0], rovers[0]), True)
problem.set_initial_value(store_of(stores[1], rovers[0]), True)
problem.set_initial_value(on_board(cameras[0], rovers[0]), True)
problem.set_initial_value(free_h(hands[0]), True)
problem.set_initial_value(free_h(hands[1]), True)
problem.set_initial_value(free_c(cameras[0]), True)
problem.set_initial_value(good(hands[0]), True)
problem.set_initial_value(hand_of(hands[0], rovers[0]), True)
problem.set_initial_value(hand_of(hands[1], rovers[0]), True)

# Goals
problem.add_goal(communicated_rock_data(rocks[0]))
problem.add_goal(communicated_rock_data(rocks[1]))
problem.add_goal(communicated_image_data(objectives[0]))

# Actions

""" sample_rock_good Action """
sample_rock_good = unified_planning.model.action.DurativeAction('sample_rock_good', rover=Rover, store=Store, rock=Rock,
                                                                hand=Hand)
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


def sample_rock_good_probability(state, actual_params):
    hand_param = actual_params.get(hand)
    rock_param = actual_params.get(rock)
    store_param = actual_params.get(store)
    rover_param = actual_params.get(rover)

    return {0.9: {full(store_param): True, have_rock_analysis(rover_param, rock_param): True, free_h(hand_param): True,
                  ready(hand_param, rock_param): False},
            0.051: {ready(hand_param, rock_param): False, free_h(hand_param): True}, 0.049: {}}


sample_rock_good.add_probabilistic_effect(
    [full(store), have_rock_analysis(rover, rock), free_h(hand), ready(hand, rock)], sample_rock_good_probability)
problem.add_action(sample_rock_good)

""" sample_rock Action """
sample_rock = unified_planning.model.action.DurativeAction('sample_rock', rover=Rover, store=Store, rock=Rock,
                                                           hand=Hand)
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


def sample_rock_probability(state, actual_params):
    hand_param = actual_params.get(hand)
    rock_param = actual_params.get(rock)
    store_param = actual_params.get(store)
    rover_param = actual_params.get(rover)

    return {0.7: {full(store_param): True, have_rock_analysis(rover_param, rock_param): True, free_h(hand_param): True,
                  ready(hand_param, rock_param): False},
            0.05: {ready(hand_param, rock_param): False, free_h(hand_param): True}, 0.25: {}}


sample_rock.add_probabilistic_effect([full(store), have_rock_analysis(rover, rock), free_h(hand), ready(hand, rock)],
                                     sample_rock_probability)
problem.add_action(sample_rock)

""" drop Action """
drop = unified_planning.model.action.DurativeAction('drop', store=Store)
drop.set_fixed_duration(3)
store = drop.parameter('store')
drop.add_precondition(OverallPreconditionTiming(), ready_to_drop(store), True)
drop.add_effect(full(store), False)
drop.add_effect(ready_to_drop(store), False)
problem.add_action(drop)

""" calibrate Action """
calibrate = unified_planning.model.action.DurativeAction('calibrate', camera=Camera, objective=Objective)
calibrate.set_fixed_duration(4)
camera = calibrate.parameter('camera')
objective = calibrate.parameter('objective')
calibrate.add_effect(calibrated(camera, objective), True)
problem.add_action(calibrate)

""" turn_on_dropping Action """
turn_on_dropping = unified_planning.model.action.DurativeAction('turn_on_dropping', store=Store)
turn_on_dropping.set_fixed_duration(1)
store = turn_on_dropping.parameter('store')
turn_on_dropping.add_effect(ready_to_drop(store), True)
problem.add_action(turn_on_dropping)

""" turn_on_good_hand Action """
turn_on_good_hand = unified_planning.model.action.DurativeAction('turn_on_good_hand', hand=Hand, rock=Rock)
turn_on_good_hand.set_fixed_duration(1)
hand = turn_on_good_hand.parameter('hand')
rock = turn_on_good_hand.parameter('rock')
turn_on_good_hand.add_precondition(StartPreconditionTiming(), free_h(hand), True)
turn_on_good_hand.add_precondition(OverallPreconditionTiming(), good(hand), True)
turn_on_good_hand.add_start_effect(free_h(hand), False)
turn_on_good_hand.add_effect(ready(hand, rock), True)
problem.add_action(turn_on_good_hand)

""" turn_on_hand Action """
turn_on_hand = unified_planning.model.action.InstantaneousAction('turn_on_hand', hand=Hand, rock=Rock)
hand = turn_on_hand.parameter('hand')
rock = turn_on_hand.parameter('rock')
turn_on_hand.add_precondition(free_h(hand), True)
turn_on_hand.add_precondition(good(hand), False)

def turn_on_hand_probability(state, actual_params):
    hand_param = actual_params.get(hand)
    rock_param = actual_params.get(rock)

    return {0.8: {free_h(hand_param): False, ready(hand_param, rock_param): True}, 0.2: {}}


turn_on_hand.add_probabilistic_effect([free_h(hand), ready(hand, rock)], turn_on_hand_probability)
problem.add_action(turn_on_hand)


""" take_image Action """
take_image = unified_planning.model.action.DurativeAction('take_image', rover=Rover, objective=Objective, camera=Camera)
take_image.set_fixed_duration(6)
rover = take_image.parameter('rover')
objective = take_image.parameter('objective')
camera = take_image.parameter('camera')
take_image.add_precondition(OverallPreconditionTiming(), calibrated(camera, objective), True)
take_image.add_precondition(OverallPreconditionTiming(), on_board(camera, rover), True)

def take_image_probability(state, actual_params):
    rover_param = actual_params.get(rover)
    objective_param = actual_params.get(objective)
    camera_param = actual_params.get(camera)

    return {0.9: {have_image(rover_param, objective_param): True, calibrated(camera_param, objective_param): False}, 0.1: {have_image(rover_param, objective_param): False, calibrated(camera_param, objective_param): False}}


take_image.add_probabilistic_effect([have_image(rover, objective), calibrated(camera, objective)], take_image_probability)
problem.add_action(take_image)


""" communicate_rock_data Action """
communicate_rock_data = unified_planning.model.action.DurativeAction('communicate_rock_data', rover=Rover, rock=Rock)
communicate_rock_data.set_fixed_duration(2)
rover = communicate_rock_data.parameter('rover')
rock = communicate_rock_data.parameter('rock')
communicate_rock_data.add_precondition(OverallPreconditionTiming(), have_rock_analysis(rover, rock), True)

def communicate_rock_data_probability(state, actual_params):
    rock_param = actual_params.get(rock)

    return {0.6: {communicated_rock_data(rock_param): True}, 0.4: {communicated_rock_data(rock_param): False}}


communicate_rock_data.add_probabilistic_effect([communicated_rock_data(rock)], communicate_rock_data_probability)
problem.add_action(communicate_rock_data)


""" communicate_image_data Action """
communicate_image_data = unified_planning.model.action.DurativeAction('communicate_image_data', rover=Rover, objective=Objective)
communicate_image_data.set_fixed_duration(2)
rover = communicate_image_data.parameter('rover')
objective = communicate_image_data.parameter('objective')
communicate_image_data.add_precondition(OverallPreconditionTiming(), have_image(rover, objective), True)

def communicate_image_data_probability(state, actual_params):
    objective_param = actual_params.get(objective)

    return {0.6: {communicated_image_data(objective_param): True}, 0.4: {communicated_image_data(objective_param): False}}


communicate_image_data.add_probabilistic_effect([communicated_image_data(objective)], communicate_image_data_probability)
problem.add_action(communicate_image_data)





deadline = Timing(delay=40, timepoint=Timepoint(TimepointKind.START))
problem.set_deadline(deadline)

# print(problem)

grounder = unified_planning.engines.compilers.Grounder()
grounding_result = grounder._compile(problem)
ground_problem = grounding_result.problem


convert_problem = unified_planning.engines.Convert_problem(ground_problem)
# print(convert_problem)
converted_problem = convert_problem._converted_problem
mdp = unified_planning.engines.MDP(converted_problem, discount_factor=0.95)

up.engines.solvers.mcts.plan(mdp, steps=90, search_depth=40, exploration_constant=10)
