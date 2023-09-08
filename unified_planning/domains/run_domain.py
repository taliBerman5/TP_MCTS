import unified_planning as up
from unified_planning.shortcuts import *

domains = dict(machine_shop=up.domains.Machine_Shop, nasa_rover=up.domains.Nasa_Rover, stuck_car=up.domains.Stuck_Car)


def run_regular(domain, deadline, search_time, search_depth, selection_type='avg'):
    assert domain in domains
    model = domains[domain](kind='regular', deadline=deadline)
    grounder = up.engines.compilers.Grounder()
    grounding_result = grounder._compile(model.problem)
    ground_problem = grounding_result.problem

    convert_problem = Convert_problem(ground_problem)
    converted_problem = convert_problem._converted_problem
    mdp = MDP(converted_problem, discount_factor=0.95)
    up.engines.solvers.mcts.plan(mdp, steps=90, search_depth=search_depth, exploration_constant=50,
                                 search_time=search_time, selection_type=selection_type)


def run_combination(domain, solver, deadline, search_time, search_depth, selection_type='avg'):
    assert domain in domains
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
        up.engines.solvers.rtdp.plan(mdp, split_mdp, steps=90, search_depth=search_depth, search_time=search_time)
    else:
        up.engines.solvers.mcts.combination_plan(mdp, split_mdp=split_mdp, steps=90, search_depth=search_time,
                                                 exploration_constant=50, search_time=search_time,
                                                 selection_type=selection_type)


if up.args.baseline:
    run_combination(domain=up.args.domain, solver='rtdp', deadline=up.args.deadline, search_time=up.args.search_time,
                    search_depth=up.args.search_depth)
else:
    run_regular(domain=up.args.domain, deadline=up.args.deadline, search_time=up.args.search_time,
                search_depth=up.args.search_depth,
                selection_type=up.args.selection_type)
