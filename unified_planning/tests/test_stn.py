import unified_planning
from unified_planning.shortcuts import *
import unittest


class TestSTN(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        problem = unified_planning.model.Problem('test_problem')

        goal = unified_planning.model.Fluent('goal', BoolType())
        problem.add_fluent(goal)
        problem.set_initial_value(goal, False)

        """ Actions """

        """ long_action Action """
        long_action = unified_planning.model.DurativeAction('long_action')
        long_action.set_fixed_duration(5)
        problem.add_action(long_action)

        """ short Action """
        short_action = unified_planning.model.DurativeAction('short_action')
        short_action.set_fixed_duration(2)
        problem.add_action(short_action)

        """ very_long_action Action """
        very_long_action = unified_planning.model.DurativeAction('very_long_action')
        very_long_action.add_start_effect(goal, True)
        very_long_action.set_fixed_duration(7)
        problem.add_action(very_long_action)


        """ very_short_action Action """
        very_short_action = unified_planning.model.DurativeAction('very_short_action')
        very_short_action.add_start_effect(goal, True)
        very_short_action.set_fixed_duration(1)
        problem.add_action(very_short_action)

        """ very_short_action2 Action """
        very_short_action2 = unified_planning.model.DurativeAction('very_short_action2')
        very_short_action2.add_start_effect(goal, True)
        very_short_action2.set_fixed_duration(1)
        problem.add_action(very_short_action2)

        deadline = Timing(delay=6, timepoint=Timepoint(TimepointKind.START))
        problem.set_deadline(deadline)
        problem.add_goal(goal)

        grounder = unified_planning.engines.compilers.Grounder()
        grounding_result = grounder._compile(problem)
        ground_problem = grounding_result.problem

        convert_problem = unified_planning.engines.Convert_problem(ground_problem)

        cls.converted_problem = convert_problem._converted_problem
        cls.mdp = unified_planning.engines.MDP(cls.converted_problem, discount_factor=10)

        cls.a_start_short = cls.converted_problem.action_by_name("start_short_action")
        cls.a_end_short = cls.converted_problem.action_by_name("end_short_action")

        cls.a_start_long = cls.converted_problem.action_by_name("start_long_action")
        cls.a_end_long = cls.converted_problem.action_by_name("end_long_action")

        cls.a_start_very_long = cls.converted_problem.action_by_name("start_very_long_action")
        cls.a_end_very_long = cls.converted_problem.action_by_name("end_very_long_action")

        cls.a_start_very_short = cls.converted_problem.action_by_name("start_very_short_action")
        cls.a_end_very_short = cls.converted_problem.action_by_name("end_very_short_action")

        cls.a_start_very_short2 = cls.converted_problem.action_by_name("start_very_short_action2")
        cls.a_end_very_short2 = cls.converted_problem.action_by_name("end_very_short_action2")

    def setUp(self) -> None:
        self.stn = create_init_stn(self.mdp)
    def test_long_before_short(self):
        print("Running test_long_before_short...")

        # Long action can not end before a short action
        node = update_stn(self.stn, self.a_start_short)
        node = update_stn(self.stn, self.a_start_long, node)
        node = update_stn(self.stn, self.a_end_long, node)
        # node = update_stn(stn, a_end_short, node)

        self.assertFalse(self.stn.is_consistent(), 'Long action cannot end before the short action')


    def test_long_short_combinations(self):
        print("Running test_long_short_combinations...")

        stn_copy = self.stn.clone()

        node = update_stn(self.stn, self.a_start_long)
        node_short = update_stn(self.stn, self.a_start_short, node)
        node = update_stn(self.stn, self.a_end_long, node_short)
        node = update_stn(self.stn, self.a_end_short, node)

        node = update_stn(stn_copy, self.a_start_long)
        node_short_copy = update_stn(stn_copy, self.a_start_short, node)
        node = update_stn(stn_copy, self.a_end_short, node_short_copy)
        node = update_stn(stn_copy, self.a_end_long, node)



        self.assertTrue(self.stn.get_legal_interval(node_short) == (3,4), 'the legal interval should be []')
        self.assertTrue(stn_copy.get_legal_interval(node_short_copy) == (0,4), 'the legal interval should be []')


    def test_long_ends_before_short(self):
        print("Running test_long_before_short...")

        # Long action can not end before a short action
        node = update_stn(self.stn, self.a_start_long)
        self.assertTrue(self.stn.get_upper_bound_node(node) == 6, 'start long can be no later than 6')

        node1 = update_stn(self.stn, self.a_start_short, node)
        self.assertTrue(self.stn.get_upper_bound_node(node) == 6, 'start long can be no later than 6')
        self.assertTrue(self.stn.get_upper_bound_node(node1) == 6, 'start short can be no later than 6')

        node2 = update_stn(self.stn, self.a_end_long, node1)
        self.assertTrue(self.stn.get_upper_bound_node(node) == 1, 'start long can be no later than 1')
        self.assertTrue(self.stn.get_upper_bound_node(node1) == 6, 'start short can be no later than 6')
        self.assertTrue(self.stn.get_upper_bound_node(node2) == 6, 'end long can be no later than 6')

        node3 = update_stn(self.stn, self.a_end_short, node2)
        self.assertTrue(self.stn.get_upper_bound_node(node) == 1, 'start long can be no later than 1')
        self.assertTrue(self.stn.get_upper_bound_node(node1) == 4, 'start short can be no later than 1')
        self.assertTrue(self.stn.get_upper_bound_node(node2) == 6, 'end long can be no later than 6')
        self.assertTrue(self.stn.get_upper_bound_node(node3) == 6, 'end short can be no later than 6')



        self.assertTrue(self.stn.is_consistent(), 'Long action can end before the short action')


    def test_long_after_short(self):
        print("Running test_long_after_short...")

        node = update_stn(self.stn, self.a_start_short)
        self.assertTrue(self.stn.get_upper_bound_node(node) == 6, 'start short can be no later than 6')

        node1 = update_stn(self.stn, self.a_start_long, node)
        self.assertTrue(self.stn.get_upper_bound_node(node1) == 6, 'start long can be no later than 6')

        node2 = update_stn(self.stn, self.a_end_short, node1)
        self.assertTrue(self.stn.get_upper_bound_node(node) == 4, 'start short can be no later than 4')
        self.assertTrue(self.stn.get_upper_bound_node(node1) == 6, 'start long can be no later than 4')
        self.assertTrue(self.stn.get_upper_bound_node(node2) == 6, 'end short can be no later than 6')

        node3 = update_stn(self.stn, self.a_end_long, node2)

        self.assertTrue(self.stn.get_upper_bound_node(node) == 1, 'start short can be no later than 1')
        self.assertTrue(self.stn.get_upper_bound_node(node1) == 1, 'start long can be no later than 1')
        self.assertTrue(self.stn.get_upper_bound_node(node2) == 3, 'end short can be no later than 3')
        self.assertTrue(self.stn.get_upper_bound_node(node3) == 6, 'end long can be no later than 6')
        self.assertTrue(self.stn.is_consistent(), 'Long action can end after the short action')


    def test_longer_than_deadline(self):
        print("Running test_longer_than_deadline...")

        node = update_stn(self.stn, self.a_start_very_long)
        self.assertTrue(self.stn.is_consistent(), 'If the end action is not chosen it can end after the end plan')

        node = update_stn(self.stn, self.a_end_very_long, node)
        self.assertFalse(self.stn.is_consistent(), 'The deadline is 6 and the action is 7 seconds')

    def test_shorter_than_deadline(self):
        print("Running test_shorter_than_deadline...")

        node = update_stn(self.stn, self.a_start_long)
        node = update_stn(self.stn, self.a_end_long, node)

        self.assertTrue(self.stn.is_consistent(), 'The deadline is 6 and the action is 5 seconds')

    def test_potential_actions(self):
        print("Running test_potential_actions...")

        node_end_long = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.END, up.plans.plan.ActionInstance(self.a_end_long, ()))

        node = update_stn(self.stn, self.a_start_long)
        end_potential = list(self.stn._potential_end_actions.keys())
        node_end_long = end_potential[end_potential.index(node_end_long)]

        self.assertTrue(node_end_long in self.stn._potential_end_actions, 'when a start action is chosen, the end action inserted to the potential end actions')

        node = update_stn(self.stn, self.a_end_long, node)
        self.assertFalse(node_end_long in self.stn._potential_end_actions, 'When the end action is chosen it is removed from the potential end actions')


    def test_goal_in_start_effect(self):
        print("Running test_goal_in_start_effect...")

        node = update_stn(self.stn, self.a_start_very_long)

        self.assertTrue(self.stn.is_consistent,
                        'only the start action is inserted')
        terminal, next_state, reward = self.mdp.step(self.mdp.initial_state(), self.a_start_very_long)

        self.assertTrue(terminal,
                        'if the goal is achieved and the plan is consistent this is a terminal state')

    def test_legal_interval(self):
        print("Running test_legal_interval...")

        node = update_stn(self.stn, self.a_start_short)
        self.stn.fix_action_time(node, 2)
        node = update_stn(self.stn, self.a_end_short, node)

        self.assertTrue(self.stn.get_legal_interval(node)==(4,4), 'The deadline is 6 and the action is 5 seconds')

    def test_legal_interval_same_action(self):
        print("Running test_legal_interval...")

        node1 = update_stn(self.stn, self.a_start_short)
        node = update_stn(self.stn, self.a_end_short, node1)
        node = update_stn(self.stn, self.a_start_short, node)
        node = update_stn(self.stn, self.a_end_short, node)

        self.assertTrue(self.stn.get_legal_interval(node)==(4,6), 'The deadline is 6')


if __name__ == '__main__':
    unittest.main()







