import unified_planning
from unified_planning.shortcuts import *


problem = unified_planning.model.Problem('stuck_car')

""" Init things that can be pushed """
Car = UserType('Car')
car = unified_planning.model.Object('car', Car)
problem.add_object(car)

GasPedal = UserType('GasPedal')
gasPedal = unified_planning.model.Object('gasPedal', GasPedal)
problem.add_object(gasPedal)

""" Init rocks """
Rock = UserType('Rock')
rocks_names = ['bad', 'good']
rocks = [unified_planning.model.Object(r, Rock) for r in rocks_names]
problem.add_objects(rocks)

""" Init body parts -
    when performing an action at least one of the body parts will be occupied
"""
BodyPart = UserType('BodyPart')
bodyParts_names = ['hands', 'legs']
bodyParts = [unified_planning.model.Object(b, BodyPart) for b in bodyParts_names]
problem.add_objects(bodyParts)

car_out = unified_planning.model.Fluent('car_out', BoolType())
problem.add_fluent(car_out)
problem.set_initial_value(car_out, False)

tired = unified_planning.model.Fluent('tired', BoolType())
problem.add_fluent(tired)
problem.set_initial_value(tired, False)

got_rock = unified_planning.model.Fluent('got_rock', BoolType(), r=Rock)
problem.add_fluent(got_rock, default_initial_value=False)

free = unified_planning.model.Fluent('free', BoolType(), b=BodyPart)
problem.add_fluent(free, default_initial_value=True)

rock_under_car = unified_planning.model.Fluent('rock_under_car', BoolType(), r=Rock)
problem.add_fluent(rock_under_car, default_initial_value=False)

""" Actions """

""" Rest Action """
rest = unified_planning.model.DurativeAction('rest')
rest.add_precondition(OverallPreconditionTiming(), free(bodyParts[0]), True)
rest.add_precondition(OverallPreconditionTiming(), free(bodyParts[1]), True)
rest.set_fixed_duration(1)
rest.add_effect(tired, False)
problem.add_action(rest)

""" Place a rock under the car Action """
place_rock = unified_planning.model.DurativeAction('place_rock', rock=Rock)
rock = place_rock.parameter('rock')
place_rock.set_fixed_duration(3)
place_rock.add_precondition(OverallPreconditionTiming(), got_rock(rock), True)

place_rock.add_precondition(StartPreconditionTiming(), free(bodyParts[0]), True)
place_rock.add_precondition(StartPreconditionTiming(), free(bodyParts[1]), True)

place_rock.add_start_effect(free(bodyParts[0]), False)
place_rock.add_start_effect(free(bodyParts[1]), False)

place_rock.add_effect(free(bodyParts[0]), True)
place_rock.add_effect(free(bodyParts[1]), True)

tired_exp = problem.get_fluent_exp(tired)
def tired_probability(state, actual_params):
    p = 0.4
    return {p: {tired_exp: True}, 1-p: {tired_exp: False}}


place_rock.add_effect(rock_under_car(rock), True)
place_rock.add_effect(got_rock(rock), False)
place_rock.add_probabilistic_effect([tired], tired_probability)
problem.add_action(place_rock)

""" Search a rock Action
    the robot can find a one of the rocks"""
search = unified_planning.model.action.DurativeAction('search')
search.set_fixed_duration(3)

search.add_precondition(StartPreconditionTiming(), free(bodyParts[0]), True)
search.add_precondition(StartPreconditionTiming(), free(bodyParts[1]), True)

search.add_start_effect(free(bodyParts[0]), False)
search.add_start_effect(free(bodyParts[1]), False)

search.add_effect(free(bodyParts[0]), True)
search.add_effect(free(bodyParts[1]), True)

# import inspect as i
got_rock_0_exp = problem.get_fluent_exp(got_rock(rocks[0]))
got_rock_1_exp = problem.get_fluent_exp(got_rock(rocks[1]))
def rock_probability(state, actual_params):
    # The probability of finding a good rock when searching
    p = 0.8
    return {p: {got_rock_0_exp: True, got_rock_1_exp: False}, 1-p: {got_rock_0_exp: False, got_rock_1_exp: True}}


search.add_probabilistic_effect([got_rock(rocks[0]), got_rock(rocks[1])], rock_probability)
problem.add_action(search)

""" Push Actions """

""" Push Gas Pedal Action """
push_gas = unified_planning.model.action.DurativeAction('push_gas')
push_gas.set_fixed_duration(2)

push_gas.add_precondition(StartPreconditionTiming(), free(bodyParts[1]), True)
push_gas.add_start_effect(free(bodyParts[1]), False)
push_gas.add_effect(free(bodyParts[1]), True)


rock_0_under_exp = problem.get_fluent_exp(rock_under_car(rocks[0]))
rock_1_under_exp = problem.get_fluent_exp(rock_under_car(rocks[1]))
car_out_exp = problem.get_fluent_exp(car_out)
def push_gas_probability(state, actual_params):
    # The probability of getting the car out when pushing the gas padel
    p = 1
    predicates = state.predicates

    if car_out_exp not in predicates:
        # The bad rock is under the car
        if rock_0_under_exp in predicates:
            p = 0.8

        # The good rock is under the car
        elif rock_1_under_exp in predicates:
            p = 0.8

        # There isn't a rock under the car
        else:
            p = 0.8

    return {p: {car_out_exp: True}, 1 - p: {car_out_exp: False}}

push_gas.add_probabilistic_effect([car_out], push_gas_probability)

problem.add_action(push_gas)

""" Push Car Action """
push_car = unified_planning.model.action.DurativeAction('push_car')
push_car.set_fixed_duration(2)

push_car.add_precondition(StartPreconditionTiming(), free(bodyParts[0]), True)
push_car.add_start_effect(free(bodyParts[0]), False)
push_car.add_effect(free(bodyParts[0]), True)

def push_car_probability(state, actual_params):
    # The probability of getting the car out when pushing the car
    p = 1
    predicates = state.predicates

    if car_out_exp not in predicates:
        # The bad rock is under the car
        if rock_0_under_exp in predicates:
            p = 0.8

        # The good rock is under the car
        elif rock_1_under_exp in predicates:
            p = 0.8

        # There isn't a rock under the car
        else:
            p = 0.8

    return {p: {car_out_exp: True}, 1 - p: {car_out_exp: False}}

push_car.add_probabilistic_effect([car_out], push_car_probability)
push_car.add_probabilistic_effect([tired], tired_probability)

problem.add_action(push_car)


problem.add_goal(car_out)
deadline = Timing(delay=6, timepoint=Timepoint(TimepointKind.START))
problem.set_deadline(deadline)

# print(problem)


grounder = unified_planning.engines.compilers.Grounder()
grounding_result = grounder._compile(problem)
ground_problem = grounding_result.problem


convert_problem = unified_planning.engines.Convert_problem(ground_problem)
print(convert_problem)
converted_problem = convert_problem.converted_problem
mdp = unified_planning.engines.MDP(converted_problem, discount_factor=10)
state = mdp.initial_state()
mdp.step(state, converted_problem.actions[0])

up.engines.mcts.plan(mdp, steps=10, search_depth=10, exploration_constant=10)