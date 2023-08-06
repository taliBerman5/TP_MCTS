import unified_planning
from unified_planning.shortcuts import *

problem = unified_planning.model.Problem('machine_shop')

""" Init piece """
Piece = UserType('Piece')
piece_names = ['x1', 'x2']
pieces = [unified_planning.model.Object(p, Piece) for p in piece_names]
problem.add_objects(pieces)

""" Init machine """
Machine = UserType('Machine')
machine_names = ['m1', 'm2']
machines = [unified_planning.model.Object(m, Machine) for m in machine_names]
problem.add_objects(machines)

# Predicates
shaped = unified_planning.model.Fluent('shaped', BoolType(), p=Piece)
problem.add_fluent(shaped, default_initial_value=False)

painted = unified_planning.model.Fluent('painted', BoolType(), p=Piece)
problem.add_fluent(painted, default_initial_value=False)

smooth = unified_planning.model.Fluent('smooth', BoolType(), p=Piece)
problem.add_fluent(smooth, default_initial_value=False)

polished = unified_planning.model.Fluent('polished', BoolType(), p=Piece)
problem.add_fluent(polished, default_initial_value=False)

canpolpaint = unified_planning.model.Fluent('canpolpaint', BoolType(), m=Machine)
problem.add_fluent(canpolpaint, default_initial_value=False)

canlatroll = unified_planning.model.Fluent('canlatroll', BoolType(), m=Machine)
problem.add_fluent(canlatroll, default_initial_value=False)

cangrind = unified_planning.model.Fluent('cangrind', BoolType(), m=Machine)
problem.add_fluent(cangrind, default_initial_value=False)

hasimmersion = unified_planning.model.Fluent('hasimmersion', BoolType(), m=Machine)
problem.add_fluent(hasimmersion, default_initial_value=False)

free = unified_planning.model.Fluent('free', BoolType(), m=Machine)
problem.add_fluent(free, default_initial_value=False)

at = unified_planning.model.Fluent('at', BoolType(), p=Piece, m=Machine)
problem.add_fluent(at, default_initial_value=False)

on = unified_planning.model.Fluent('on', BoolType(), p=Piece, m=Machine)
problem.add_fluent(on, default_initial_value=False)

problem.set_initial_value(at(pieces[0], machines[1]), True)
problem.set_initial_value(at(pieces[1], machines[1]), True)
problem.set_initial_value(canpolpaint(machines[0]), True)
problem.set_initial_value(canlatroll(machines[1]), True)
problem.set_initial_value(cangrind(machines[1]), True)
problem.set_initial_value(free(machines[0]), True)
problem.set_initial_value(free(machines[1]), True)

# Goals
problem.add_goal(shaped(pieces[0]))
problem.add_goal(painted(pieces[1]))
problem.add_goal(smooth(pieces[0]))
problem.add_goal(polished(pieces[1]))
problem.add_goal(free(machines[0]))
problem.add_goal(free(machines[1]))

# Actions

""" Polish Action """
polish = unified_planning.model.action.DurativeAction('polish', piece=Piece, machine=Machine)
polish.set_fixed_duration(10)
machine = polish.parameter('machine')
piece = polish.parameter('piece')
polish.add_precondition(StartPreconditionTiming(), canpolpaint(machine), True)
polish.add_precondition(OverallPreconditionTiming(), on(piece, machine), True)
polish.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)

def polish_probability(state, actual_params):
    piece_param = actual_params.get(piece)
    p = 0.9
    return {p: {polished(piece_param): True}, 1 - p: {}}


polish.add_probabilistic_effect([polished(piece)], polish_probability)
problem.add_action(polish)

""" Spraypaint Action """
spraypaint = unified_planning.model.action.DurativeAction('spraypaint', piece=Piece, machine=Machine)
spraypaint.set_fixed_duration(6)
machine = spraypaint.parameter('machine')
piece = spraypaint.parameter('piece')
spraypaint.add_precondition(StartPreconditionTiming(), canpolpaint(machine), True)
spraypaint.add_precondition(OverallPreconditionTiming(), on(piece, machine), True)
spraypaint.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)

def spraypaint_probability(state, actual_params):
    piece_param = actual_params.get(piece)
    p = 0.8

    return {p: {painted(piece_param): True}, 1 - p: {}}


spraypaint.add_probabilistic_effect([painted(piece)], spraypaint_probability)
problem.add_action(spraypaint)

""" Immersionpaint Action """
immersionpaint = unified_planning.model.action.DurativeAction('immersionpaint', piece=Piece, machine=Machine)
immersionpaint.set_fixed_duration(4)
machine = immersionpaint.parameter('machine')
piece = immersionpaint.parameter('piece')
immersionpaint.add_precondition(StartPreconditionTiming(), canpolpaint(machine), True)
immersionpaint.add_precondition(OverallPreconditionTiming(), on(piece, machine), True)
immersionpaint.add_precondition(OverallPreconditionTiming(), hasimmersion(machine), True)
immersionpaint.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)


def immersionpaint_probability(state, actual_params):
    piece_param = actual_params.get(piece)
    machine_param = actual_params.get(machine)
    return {0.57: {painted(piece_param): True},
                0.38: {painted(piece_param): True, hasimmersion(machine_param): False},
                0.02: {hasimmersion(machine_param): False}, 0.03: {}}


immersionpaint.add_probabilistic_effect([painted(piece), hasimmersion(machine)], immersionpaint_probability)
problem.add_action(immersionpaint)

""" Lathe Action """
lathe = unified_planning.model.action.DurativeAction('lathe', piece=Piece, machine=Machine)
lathe.set_fixed_duration(2)
machine = lathe.parameter('machine')
piece = lathe.parameter('piece')
lathe.add_precondition(StartPreconditionTiming(), canlatroll(machine), True)
lathe.add_precondition(OverallPreconditionTiming(), on(piece, machine), True)
lathe.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)


def lathe_probability(state, actual_params):
    piece_param = actual_params.get(piece)
    predicates = state.predicates
    p = 0.9

    return {p: {shaped(piece_param): True, painted(piece_param): False, smooth(piece_param): False}, 1 - p: {}}


lathe.add_probabilistic_effect([shaped(piece), painted(piece), smooth(piece)], lathe_probability)
problem.add_action(lathe)

""" Grind Action """
grind = unified_planning.model.action.DurativeAction('grind', piece=Piece, machine=Machine)
grind.set_fixed_duration(3)
machine = grind.parameter('machine')
piece = grind.parameter('piece')
grind.add_precondition(StartPreconditionTiming(), cangrind(machine), True)
grind.add_precondition(OverallPreconditionTiming(), on(piece, machine), True)
grind.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)


def grind_probability(state, actual_params):
    piece_param = actual_params.get(piece)
    p = 0.9

    return {p: {smooth(piece_param): True}, 1 - p: {}}


grind.add_probabilistic_effect([smooth(piece)], grind_probability)
problem.add_action(grind)

""" Buyimmersion Action """
buyimmersion = unified_planning.model.action.DurativeAction('buyimmersion', machine=Machine)
buyimmersion.set_fixed_duration(5)
machine = buyimmersion.parameter('machine')

buyimmersion.add_effect(hasimmersion(machine), True)
problem.add_action(buyimmersion)

""" Place Action """
place = unified_planning.model.action.DurativeAction('place', piece=Piece, machine=Machine)
place.set_fixed_duration(1)
machine = place.parameter('machine')
piece = place.parameter('piece')
place.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)
place.add_precondition(StartPreconditionTiming(), free(machine), True)
place.add_effect(on(piece, machine), True)
place.add_start_effect(free(machine), False)
problem.add_action(place)

""" Move Action """
move = unified_planning.model.action.DurativeAction('move', piece=Piece, machine1=Machine, machine2=Machine)
move.set_fixed_duration(3)
machine1 = move.parameter('machine1')
machine2 = move.parameter('machine2')
piece = move.parameter('piece')
move.add_precondition(ParamPrecondition(), Equals(machine1, machine2),  False)
move.add_precondition(StartPreconditionTiming(), at(piece, machine1), True)
move.add_start_effect(at(piece, machine1), False)

def move_probability(state, actual_params):
    p = 0
    piece_param = actual_params.get(piece)
    machine1_param = actual_params.get(machine1)
    machine2_param = actual_params.get(machine2)
    predicates = state.predicates
    if on(piece_param, machine1_param) in predicates:
        p = 0.9
        return {p: {at(piece_param, machine2_param): True,
                    on(piece_param, machine1_param): False, free(machine1_param): True},
                1 - p: {on(piece_param, machine1_param): False, free(machine1_param): True, at(piece_param, machine1_param): True}}
    else:
        p = 0.9
        return {p: {at(piece_param, machine2_param): True}, 1 - p: {at(piece_param, machine1_param): True}}



move.add_probabilistic_effect([on(piece, machine1), free(machine2), at(piece, machine1), at(piece, machine2)], move_probability)
problem.add_action(move)



deadline = Timing(delay=25, timepoint=Timepoint(TimepointKind.START))
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