import unified_planning as up
from unified_planning.shortcuts import *
import unittest

from unified_planning.tests import mutex_converted_problem, OAP_converted_problem


class Test_Converted_Problem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mutex_converted_problem = mutex_converted_problem
        cls.OAP_converted_problem = OAP_converted_problem


    # def setUp(self) -> None:

    def test_amount_actions(self):
        print("Running test_amount_actions...")
        self.assertTrue(len(self.mutex_converted_problem.actions) == 10, 'each durative action needs to be splitted to start and end actions')
    def test_soft_mutex(self):
        print("Running test_soft_mutex...")

        soft_mutex = self.mutex_converted_problem.action_by_name('end_soft_mutex')
        start_action_object = self.mutex_converted_problem.object_by_name('start-a')
        in_execution = self.mutex_converted_problem.fluents[-1]
        self.assertTrue(in_execution(start_action_object) in soft_mutex.neg_preconditions, 'soft mutex need to appear')

    def test_mutex(self):
        print("Running test_mutex...")

        start_a_object = self.mutex_converted_problem.object_by_name('start-a')
        start_mutex= self.mutex_converted_problem.action_by_name('start_mutex')
        insta_mutex = self.mutex_converted_problem.action_by_name('insta_mutex')
        in_execution = self.mutex_converted_problem.fluents[-1]

        self.assertTrue(in_execution(start_a_object) in start_mutex.neg_preconditions, 'cant run in parallel with mutex action')
        self.assertTrue(in_execution(start_a_object) in insta_mutex.neg_preconditions, 'cant run in parallel with mutex action')

    def test_overall_precondition(self):
        print("Running test_overall_precondition...")

        start_a = self.OAP_converted_problem.action_by_name('start_removed_overAll')
        start_b = self.OAP_converted_problem.action_by_name('start_keep_overAll')
        effect = list(self.OAP_converted_problem.initial_values.keys())[0]
        self.assertFalse(effect in start_a.neg_preconditions, 'effect should not be a precondition')
        self.assertTrue(effect in start_b.neg_preconditions, 'effect should be a precondition')


if __name__ == '__main__':
    unittest.main()



