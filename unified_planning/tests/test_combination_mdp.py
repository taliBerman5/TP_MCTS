import unified_planning as up
from unified_planning.shortcuts import *
import unittest

from unified_planning.tests import combination_converted_problem


class Test_Combination_MDP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.combination_converted_problem = combination_converted_problem
        cls.combinationMDP = unified_planning.engines.combinationMDP(cls.combination_converted_problem,
                                                                     discount_factor=0.95)

        cls.init_state = cls.combinationMDP.initial_state()
        cls.biggest_combination = combination_converted_problem.action_by_name('second_3,second_1,second_5')

        cls.start_second_1 = combination_converted_problem.object_by_name('start-second_1')
        cls.start_second_3 = combination_converted_problem.object_by_name('start-second_3')
        cls.start_second_5 = combination_converted_problem.object_by_name('start-second_5')
        cls.effect1 = combination_converted_problem.fluent_by_name('effect1')
        cls.effect3 = combination_converted_problem.fluent_by_name('effect3')
        cls.in_execution = combination_converted_problem.fluent_by_name('inExecution')

    # def setUp(self) -> None:
    #

    def test_combination_step_biggest_combination(self):
        print("Running test_combination_step_biggest_combination...")
        _, next_state, _ = self.combinationMDP.step(self.init_state, self.biggest_combination)

        # check the predicates after the step
        self.assertFalse(self.in_execution(self.start_second_1) in next_state.predicates,
                         'second_1 action is not supposed to be active')
        self.assertTrue(self.in_execution(self.start_second_3) in next_state.predicates, 'second_3 need to appear')
        self.assertTrue(self.in_execution(self.start_second_5) in next_state.predicates, 'second_5 need to appear')
        self.assertTrue(self.effect1() in next_state.predicates, 'effect1 need to appear')

        # check the delta is extracted
        for node in next_state.active_actions.data:
            self.assertTrue(node.duration_left == node.action.duration.lower.int_constant_value() - 1, 'the duration left should decrease by one')


    def test_combination_two_actions_ends(self):
        print("Running test_combination_two_actions_ends...")

        second_1 = combination_converted_problem.action_by_name('second_1')
        # second_7 = combination_converted_problem.action_by_name('second_7')

        _, next_state, _ = self.combinationMDP.step(self.init_state, self.biggest_combination)
        _, next_state, _ = self.combinationMDP.step(next_state, second_1)
        _, next_state, _ = self.combinationMDP.step(next_state, second_1)

        # check the predicates after the step
        self.assertFalse(self.in_execution(self.start_second_1) in next_state.predicates,
                         'second_1 action is not supposed to be active')
        self.assertFalse(self.in_execution(self.start_second_3) in next_state.predicates,
                         'second_3 action is not supposed to be active')
        self.assertTrue(self.in_execution(self.start_second_5) in next_state.predicates, 'second_5 need to appear')
        self.assertTrue(self.effect1() in next_state.predicates, 'effect1 need to appear')
        self.assertTrue(self.effect3() in next_state.predicates, 'effect1 need to appear')

        # check the delta is extracted
        for node in next_state.active_actions.data:
            self.assertTrue(node.duration_left == node.action.duration.lower.int_constant_value() - 3, 'the duration left should decrease by 3')


    def test_combination_no_op(self):
            print("Running test_combination_no_op...")

            noop = combination_converted_problem.action_by_name('noop')

            _, next_state, _ = self.combinationMDP.step(self.init_state, self.biggest_combination)
            _, next_state, _ = self.combinationMDP.step(next_state, noop)

            # check the predicates after the step
            self.assertFalse(self.in_execution(self.start_second_1) in next_state.predicates,
                             'second_1 action is not supposed to be active')
            self.assertFalse(self.in_execution(self.start_second_3) in next_state.predicates,
                             'second_3 action is not supposed to be active')
            self.assertTrue(self.in_execution(self.start_second_5) in next_state.predicates, 'second_5 need to appear')

            # check the delta is extracted
            for node in next_state.active_actions.data:
                self.assertTrue(node.duration_left == node.action.duration.lower.int_constant_value() -3, 'the duration left should decrease by 3')

if __name__ == '__main__':
    unittest.main()
