import unified_planning
from unified_planning.shortcuts import *


mutex_problem = unified_planning.model.Problem('mutex_problem')

effect = unified_planning.model.Fluent('effect', BoolType())
mutex_problem.add_fluent(effect)
mutex_problem.set_initial_value(effect, False)

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

grounder = unified_planning.engines.compilers.Grounder()
mutex_grounding_result = grounder._compile(mutex_problem)
mutex_ground_problem = mutex_grounding_result.problem

mutex_convert_problem = unified_planning.engines.Convert_problem(mutex_ground_problem)

mutex_converted_problem = mutex_convert_problem.converted_problem