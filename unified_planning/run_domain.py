import os
import sys

"""For the bach script"""
# Get the current directory (where the script is located)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)  # Add the path to your 'unified_planning' directory

import unified_planning as up
from unified_planning.shortcuts import *
import unified_planning.domains

domains = dict(machine_shop=up.domains.Machine_Shop, nasa_rover=up.domains.Nasa_Rover, stuck_car=up.domains.Stuck_Car, strips=up.domains.Strips, strips_prob=up.domains.Strips_Prob)

def print_stats():
    print(f'Model = {up.args.domain}')
    print(f'Solver = {up.args.solver}')
    print(f'Selection Type = {up.args.selection_type}')
    print(f'Exploration Constant = {up.args.exploration_constant}')
    print(f'Search time = {up.args.search_time}')
    print(f'Search depth = {up.args.search_depth}')
    print(f'Deadline = {up.args.deadline}')
    print(f'Domain Type = {up.args.domain_type}')

def run_regular(domain, runs, domain_type, deadline, search_time, search_depth, exploration_constant, selection_type='avg'):
    assert domain in domains
    print_stats()

    model = domains[domain](kind=domain_type, deadline=deadline)
    grounder = up.engines.compilers.Grounder()
    grounding_result = grounder._compile(model.problem)
    ground_problem = grounding_result.problem

    convert_problem = Convert_problem(ground_problem)
    converted_problem = convert_problem._converted_problem
    mdp = MDP(converted_problem, discount_factor=0.95)

    params = (mdp, 90, search_time, search_depth, exploration_constant, selection_type)
    up.engines.solvers.evaluate.evaluation_loop(runs, up.engines.solvers.mcts.plan, params)


def run_combination(domain, runs, solver, deadline, search_time, search_depth, exploration_constant, selection_type='avg'):
    assert domain in domains
    print_stats()

    model = domains[domain](kind='combination', deadline=deadline)
    grounder = up.engines.compilers.Grounder()
    grounding_result = grounder._compile(model.problem)
    ground_problem = grounding_result.problem

    convert_combination_problem = Convert_problem_combination(ground_problem)
    converted_problem = convert_combination_problem._converted_problem
    model.remove_actions(converted_problem)

    mdp = combinationMDP(converted_problem, discount_factor=0.95)
    split_mdp = MDP(convert_combination_problem._split_problem, discount_factor=0.95)

    if solver == 'rtdp':
        params = (mdp, split_mdp, 90, search_time, search_depth)
        up.engines.solvers.evaluate.evaluation_loop(runs, up.engines.solvers.rtdp.plan, params)

    else:
        params = (mdp, split_mdp, 90, search_time, search_depth, exploration_constant, selection_type)
        up.engines.solvers.evaluate.evaluation_loop(runs, up.engines.solvers.mcts.combination_plan, params)


if up.args.domain_type == 'combination':
    run_combination(domain=up.args.domain, runs=up.args.runs, solver=up.args.solver, deadline=up.args.deadline, search_time=up.args.search_time,
                    search_depth=up.args.search_depth, exploration_constant=up.args.exploration_constant, selection_type=up.args.selection_type)
else:
    run_regular(domain=up.args.domain, domain_type=up.args.domain_type, runs=up.args.runs, deadline=up.args.deadline, search_time=up.args.search_time,
                search_depth=up.args.search_depth, exploration_constant=up.args.exploration_constant,
                selection_type=up.args.selection_type)
