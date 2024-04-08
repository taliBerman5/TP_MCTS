import unified_planning
from unified_planning.shortcuts import *
from unified_planning.domains import Domain

mutex_problem = unified_planning.model.Problem('mutex_problem')

effect = unified_planning.model.Fluent('effect', BoolType())
init = unified_planning.model.Fluent('init', BoolType())
mutex_problem.add_fluent(effect)
mutex_problem.add_fluent(init)
mutex_problem.set_initial_value(effect, False)
mutex_problem.set_initial_value(init, True)

""" Actions """

""" a Action """
a = unified_planning.model.DurativeAction('a')
a.add_precondition(OverallPreconditionTiming(), effect, False)
a.set_fixed_duration(3)
mutex_problem.add_action(a)

""" soft_mutex Action """
soft_mutex = unified_planning.model.DurativeAction('soft_mutex')
soft_mutex.add_effect(effect, True)
soft_mutex.set_fixed_duration(4)
mutex_problem.add_action(soft_mutex)

""" mutex Action """
mutex = unified_planning.model.DurativeAction('mutex')
mutex.add_start_effect(effect, True)
mutex.set_fixed_duration(4)
mutex_problem.add_action(mutex)

""" mutex InstantaneousAction """
insta_mutex = unified_planning.model.InstantaneousAction('insta_mutex')
insta_mutex.add_effect(effect, True)
mutex_problem.add_action(insta_mutex)


""" list check Action """
delete_init = unified_planning.model.InstantaneousAction('delete_init')
delete_init.add_effect(init, False)
mutex_problem.add_action(delete_init)

add_effect = unified_planning.model.InstantaneousAction('add_effect')
add_effect.add_effect(effect, True)
mutex_problem.add_action(add_effect)


add_init = unified_planning.model.InstantaneousAction('add_init')
add_init.add_effect(init, True)
mutex_problem.add_action(add_init)


grounder = unified_planning.engines.compilers.Grounder()
mutex_grounding_result = grounder._compile(mutex_problem)
mutex_ground_problem = mutex_grounding_result.problem

mutex_convert_problem = unified_planning.engines.Convert_problem(mutex_ground_problem)

mutex_converted_problem = mutex_convert_problem._converted_problem






OAP_problem = unified_planning.model.Problem('over_all_precondition')

effect = unified_planning.model.Fluent('effect', BoolType())
init = unified_planning.model.Fluent('init', BoolType())
OAP_problem.add_fluent(effect)
OAP_problem.add_fluent(init)
OAP_problem.set_initial_value(effect, False)
OAP_problem.set_initial_value(init, True)

""" Actions """

""" removed_overAll Action """
removed_overAll = unified_planning.model.DurativeAction('removed_overAll')
removed_overAll.add_precondition(OverallPreconditionTiming(), effect, False)
removed_overAll.add_start_effect(effect, False)
removed_overAll.set_fixed_duration(3)
OAP_problem.add_action(removed_overAll)


""" keep_overAll Action """
keep_overAll = unified_planning.model.DurativeAction('keep_overAll')
keep_overAll.add_precondition(OverallPreconditionTiming(), effect, False)
keep_overAll.add_start_effect(effect, True)
keep_overAll.set_fixed_duration(3)
OAP_problem.add_action(keep_overAll)


grounder = unified_planning.engines.compilers.Grounder()
OAP_grounding_result = grounder._compile(OAP_problem)
OAP_ground_problem = OAP_grounding_result.problem

OAP_convert_problem = unified_planning.engines.Convert_problem(OAP_ground_problem)

OAP_converted_problem = OAP_convert_problem._converted_problem


combination_problem = unified_planning.model.Problem('combination')
effect1 = unified_planning.model.Fluent('effect1', BoolType())
effect3 = unified_planning.model.Fluent('effect3', BoolType())
effect5 = unified_planning.model.Fluent('effect5', BoolType())
effect_instant = unified_planning.model.Fluent('effect_instant', BoolType())
combination_problem.add_fluent(effect1, default_initial_value=False)
combination_problem.add_fluent(effect3, default_initial_value=False)
combination_problem.add_fluent(effect5, default_initial_value=False)
combination_problem.add_fluent(effect_instant, default_initial_value=False)


second_3 = unified_planning.model.DurativeAction('second_3')
second_3.add_effect(effect3, True)
second_3.set_fixed_duration(3)
combination_problem.add_action(second_3)
second_1 = unified_planning.model.DurativeAction('second_1')
second_1.add_effect(effect1, True)
second_1.set_fixed_duration(1)
combination_problem.add_action(second_1)
second_5 = unified_planning.model.DurativeAction('second_5')
second_5.add_effect(effect5, True)
second_5.set_fixed_duration(5)
combination_problem.add_action(second_5)
# second_7 = unified_planning.model.DurativeAction('second_7')
# second_7.set_fixed_duration(7)
# combination_problem.add_action(second_7)
instant = unified_planning.model.InstantaneousAction('instant')
instant.add_effect(effect_instant, True)
combination_problem.add_action(instant)

domain = Domain('combination', 'combination')
domain.problem = combination_problem
grounder = unified_planning.engines.compilers.Grounder()
combination_grounding_result = grounder._compile(combination_problem)
combination_ground_problem = combination_grounding_result.problem

combination_convert_problem = unified_planning.engines.Convert_problem_combination(domain,combination_ground_problem)

combination_converted_problem = combination_convert_problem._converted_problem



