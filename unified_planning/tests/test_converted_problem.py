import unified_planning as up
from unified_planning.shortcuts import *
import unittest

from unified_planning.tests import mutex_converted_problem


class Test_Converted_Problem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.converted_problem = mutex_converted_problem


    # def setUp(self) -> None:

    def test_amount_actions(self):
        print("Running test_amount_actions...")
        self.assertTrue(len(self.converted_problem.actions) == 7, 'each durative action needs to be splitted to start and end actions')
    def test_soft_mutex(self):
        print("Running test_soft_mutex...")

        soft_mutex = self.converted_problem.action_by_name('end_soft_mutex')
        start_action_object = self.converted_problem.object_by_name('start-a')
        in_execution = self.converted_problem.fluents[1]
        self.assertTrue(in_execution(start_action_object) in soft_mutex.neg_preconditions, 'soft mutex need to appear')

    def test_mutex(self):
        print("Running test_mutex...")

        start_a_object = self.converted_problem.object_by_name('start-a')
        start_mutex= self.converted_problem.action_by_name('start_mutex')
        insta_mutex = self.converted_problem.action_by_name('insta_mutex')
        in_execution = self.converted_problem.fluents[1]

        self.assertTrue(in_execution(start_a_object) in start_mutex.neg_preconditions, 'cant run in parallel with mutex action')
        self.assertTrue(in_execution(start_a_object) in insta_mutex.neg_preconditions, 'cant run in parallel with mutex action')



if __name__ == '__main__':
    unittest.main()



