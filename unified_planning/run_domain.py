import os
import time

import dill
import sys

"""For the bash script"""
# Get the current directory (where the script is located)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)  # Add the path to your 'unified_planning' directory

import unified_planning as up
from unified_planning.shortcuts import *
import unified_planning.domains

domains = dict(machine_shop=up.domains.Machine_Shop, nasa_rover=up.domains.Nasa_Rover, stuck_car=up.domains.Stuck_Car,
               stuck_car_robot=up.domains.Stuck_Car_Robot, strips=up.domains.Strips, full_strips=up.domains.Full_Strips,
               strips_prob=up.domains.Strips_Prob, best_no_parallel=up.domains.Best_No_Parallel, simple=up.domains.Simple)
domains_files = dict(machine_shop="machine_shop_domain_comb", nasa_rover="nasa_rover_domain_comb",
                     stuck_car="stuck_car_domain_comb", stuck_car_robot="stuck_car_robot_domain_comb", strips="strips_domain_comb",
                     full_strips="full_strips_domain_comb", strips_prob="strips_prob_domain_comb",
                     simple="simple_domain_comb")


def print_stats():
    print(f'Model = {up.args.domain}')
    print(f'Solver = {up.args.solver}')
    print(f'Selection Type = {up.args.selection_type}')
    print(f'Exploration Constant = {up.args.exploration_constant}')
    print(f'Search time = {up.args.search_time}')
    print(f'Search depth = {up.args.search_depth}')
    print(f'Deadline = {up.args.deadline}')
    print(f'Domain Type = {up.args.domain_type}')
    print(f'Object Amount = {up.args.object_amount}')
    print(f'Garbage Action Amount = {up.args.garbage_amount}')
    print(f'K Random Actions = {up.args.k}')


def run_regular(domain, runs, domain_type, deadline, search_time, search_depth, exploration_constant, object_amount, garbage_amount,
                selection_type='avg', k=10):
    assert domain in domains
    print_stats()
    start_time = time.time()
    model = domains[domain](kind=domain_type, deadline=deadline, object_amount=object_amount, garbage_amount=garbage_amount)
    if domain == 'nasa_rover':
        grounder = up.engines.compilers.Grounder(model.grounding_map())
    else:
        grounder = up.engines.compilers.Grounder()

    grounding_result = grounder._compile(model.problem)
    ground_problem = grounding_result.problem

    convert_problem = Convert_problem(ground_problem)
    converted_problem = convert_problem._converted_problem

    end_time = time.time()

    elapsed_time = end_time - start_time

    # Print the result and elapsed time
    print(f"Compilation Time {domain} object={object_amount}, garbage={garbage_amount}: {elapsed_time} seconds")


    mdp = MDP(converted_problem, discount_factor=0.95)

    params = (mdp, 90, search_time, search_depth, exploration_constant, selection_type, k)
    up.engines.solvers.evaluate.evaluation_loop(runs, up.engines.solvers.mcts.plan, params)


def create_combination_domain(domain, deadline, object_amount, garbage_amount):
    model = domains[domain](kind='combination', deadline=deadline, object_amount=object_amount, garbage_amount=garbage_amount)
    if domain == 'nasa_rover':
        grounder = up.engines.compilers.Grounder(model.grounding_map())
    else:
        grounder = up.engines.compilers.Grounder()
    grounding_result = grounder._compile(model.problem)
    ground_problem = grounding_result.problem

    convert_combination_problem = Convert_problem_combination(model, ground_problem)
    # convert_combination_problem = Convert_problem_combination(model, ground_problem)
    converted_problem = convert_combination_problem._converted_problem
    model.remove_actions(converted_problem)

    return convert_combination_problem


def run_combination(domain, runs, solver, deadline, search_time, search_depth, exploration_constant, object_amount, garbage_amount,
                    selection_type='avg', k=10):
    assert domain in domains
    print_stats()

    file_name = './pickle_domains/' + domains_files[domain]
    if domain == 'strips_prob' or domain == 'simple':
        file_name += "_" + str(garbage_amount)
    if domain == 'nasa_rover' or domain == 'stuck_car_robot':
        file_name += "_" + str(object_amount)
    if domain == 'machine_shop':
        file_name += "_" + str(object_amount)

    file_name += '.pkl'
    try:
    # Try to load the saved object

        with open(file_name, "rb") as file:
            convert_combination_problem = dill.load(file)
            converted_problem = convert_combination_problem._converted_problem
            split_problem = convert_combination_problem._split_problem

        deadline_timing = Timing(delay=deadline, timepoint=Timepoint(TimepointKind.START))
        converted_problem.set_deadline(deadline_timing)
        split_problem.set_deadline(deadline_timing)

    except FileNotFoundError:
        # If the file doesn't exist, create a new instance from scratch
        convert_combination_problem = create_combination_domain(domain, deadline, object_amount, garbage_amount)
        converted_problem = convert_combination_problem._converted_problem
        split_problem = convert_combination_problem._split_problem

    mdp = combinationMDP(converted_problem, discount_factor=0.95)
    split_mdp = MDP(split_problem, discount_factor=0.95)

    if solver == 'rtdp':
        params = (mdp, split_mdp, 90, search_time, search_depth)
        up.engines.solvers.evaluate.evaluation_loop(runs, up.engines.solvers.rtdp.plan, params)

    else:
        params = (mdp, split_mdp, 90, search_time, search_depth, exploration_constant, selection_type, k)
        up.engines.solvers.evaluate.evaluation_loop(runs, up.engines.solvers.mcts.combination_plan, params)


if up.args.domain_type == 'combination':
    run_combination(domain=up.args.domain, runs=up.args.runs, solver=up.args.solver, deadline=up.args.deadline,
                    search_time=up.args.search_time,
                    search_depth=up.args.search_depth, exploration_constant=up.args.exploration_constant,
                    selection_type=up.args.selection_type, object_amount=up.args.object_amount, garbage_amount=up.args.garbage_amount, k=up.args.k)
else:
    run_regular(domain=up.args.domain, domain_type=up.args.domain_type, runs=up.args.runs, deadline=up.args.deadline,
                search_time=up.args.search_time,
                search_depth=up.args.search_depth, exploration_constant=up.args.exploration_constant,
                selection_type=up.args.selection_type, object_amount=up.args.object_amount, garbage_amount=up.args.garbage_amount, k=up.args.k)
