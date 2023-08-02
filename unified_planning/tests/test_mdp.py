import unified_planning
from unified_planning.shortcuts import *
import unittest
from unified_planning.tests import mutex_converted_problem

class TestMDP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.converted_problem = mutex_converted_problem
        cls.mdp = unified_planning.engines.MDP(cls.converted_problem, discount_factor=0.95)

    def test_soft_mutex_is_not_legal(self):
        print("Running test_soft_mutex_is_not_legal...")

        start_a = self.converted_problem.action_by_name("start_a")
        start_soft_mutex = self.converted_problem.action_by_name("start_soft_mutex")
        end_soft_mutex = self.converted_problem.action_by_name("end_soft_mutex")

        _, next_state, _ = self.mdp.step(self.mdp.initial_state(), start_a)
        _, next_state, _ = self.mdp.step(next_state, start_soft_mutex)

        self.assertFalse(end_soft_mutex in self.mdp.legal_actions(next_state), "soft mutex can end before action a")

    def test_pool_of_state(self):
        print("Running test_pool_of_state...")
        legal = {}

        delete_init = self.converted_problem.action_by_name("delete_init")
        add_effect = self.converted_problem.action_by_name("add_effect")
        add_init = self.converted_problem.action_by_name("add_init")

        _, next_state, _ = self.mdp.step(self.mdp.initial_state(), delete_init)
        _, next_state, _ = self.mdp.step(next_state, add_effect)
        _, next_state, _ = self.mdp.step(next_state, add_init)


        legal[next_state] = self.mdp.legal_actions(next_state)

        _, next_state2, _ = self.mdp.step(self.mdp.initial_state(), add_effect)

        self.assertTrue(next_state2 in legal)



if __name__ == '__main__':
    unittest.main()
