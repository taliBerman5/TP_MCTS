import unified_planning
from unified_planning.shortcuts import *
import unittest


class TestLinkedList(unittest.TestCase):
    def setUp(self) -> None:
        self.linkedList = LinkedList()
    def test_empty_list(self):
        print("Running test_empty_list...")

        self.linkedList.update(3, 5, 10)

        node = LinkedListNode(3, 5, 10)

        self.assertTrue(self.linkedList.count == 1, 'count should be 1')
        self.assertTrue(self.linkedList.max_value == 10, 'max value should be 10')
        self.assertTrue(self.linkedList.head == node, 'head must be equal to node')


    def test_add_before_head(self):
        print("Running test_add_before_head...")

        self.linkedList.update(3, 5, 10)
        self.linkedList.update(1, 2, 20)

        head = LinkedListNode(1, 2, 20)
        next = LinkedListNode(3, 5, 10)
        head.next = next

        self.assertTrue(self.linkedList.count == 2, 'count should be 2')
        self.assertTrue(self.linkedList.max_value == 20, 'max value should be 20')
        self.assertTrue(self.linkedList.head == head, 'head must be equal to head')


    def test_add_intersection_head(self):
        print("Running test_add_intersection_head...")

        self.linkedList.update(3, 5, 10)
        self.linkedList.update(1, 4, 20)

        head = LinkedListNode(1, 3-self.linkedList.epsilon, 20)
        next = LinkedListNode(3, 4, 30)
        next2 = LinkedListNode(4+self.linkedList.epsilon, 5, 10)
        head.next = next
        next.next = next2

        self.assertTrue(self.linkedList.count == 2, 'count should be 2')
        self.assertTrue(self.linkedList.max_value == 30, 'max value should be 30')
        self.assertTrue(self.linkedList.head == head, 'head must be equal to head')


    def test_add_intersection(self):
        print("Running test_add_intersection_head...")

        self.linkedList.update(3, 5, 10)
        self.linkedList.update(6, 8, 10)
        self.linkedList.update(9, 11, 10)
        self.linkedList.update(7, 10, 20)

        head = LinkedListNode(3, 5, 10)
        next = LinkedListNode(6, 7-self.linkedList.epsilon, 10)
        next1 = LinkedListNode(7, 8, 30)
        next2 = LinkedListNode(8 + self.linkedList.epsilon, 9 - self.linkedList.epsilon, 20)
        next3 = LinkedListNode(9, 10, 30)
        next4 = LinkedListNode(10 + self.linkedList.epsilon, 11, 10)
        head.next = next
        next.next = next1
        next1.next = next2
        next2.next = next3
        next3.next = next4

        self.assertTrue(self.linkedList.count == 4, 'count should be 4')
        self.assertTrue(self.linkedList.max_value == 30, 'max value should be 30')
        self.assertTrue(self.linkedList.head == head, 'head must be equal to head')


    def test_add_after_head(self):
        print("Running test_add_after_head...")

        self.linkedList.update(3, 5, 10)
        self.linkedList.update(6, 7, 20)

        head = LinkedListNode(3, 5, 10)
        next = LinkedListNode(6, 7, 20)
        head.next = next

        self.assertTrue(self.linkedList.count == 2, 'count should be 2')
        self.assertTrue(self.linkedList.max_value == 20, 'max value should be 20')
        self.assertTrue(self.linkedList.head == head, 'head must be equal to head')





if __name__ == '__main__':
    unittest.main()







