import unified_planning
from unified_planning.shortcuts import *
import unittest
from unified_planning.tests import mutex_converted_problem

class TestNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.converted_problem = mutex_converted_problem
        cls.mdp = unified_planning.engines.MDP(cls.converted_problem, discount_factor=0.95)
        cls.stn = create_init_stn(cls.mdp)

    def test_soft_mutex_is_not_legal(self):
        print("Running test_soft_mutex_is_not_legal...")

        state = self.mdp.initial_state()
        snode = up.engines.C_SNode(state, 0, self.mdp.legal_actions(state), self.stn, isInterval=True)
        anode = list(snode.children.values())[0]

        for i in range(3):
            backup_node = LinkedListNode(1,3, 10)
            anode.update(None, backup_node)
            backup_node = snode.max_update(backup_node)
            print(4)


        print(5)

        # self.assertFalse(end_soft_mutex in self.mdp.legal_actions(next_state), "soft mutex can end before action a")


if __name__ == '__main__':
    unittest.main()
