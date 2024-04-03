from typing import Deque, Dict, List, Optional, Any, Generic, Set, Tuple, TypeVar, cast
import math


class LinkedListNode:
    def __init__(self, lower_bound, upper_bound, value):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.value = value
        self.next: Optional["LinkedListNode"] = None


    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, LinkedListNode):
            return self.lower_bound == oth.lower_bound and \
                self.upper_bound == oth.upper_bound and self.value == oth.value and self.next == oth.next
        else:
            return False

    def update_value(self, reward):
        self.value += reward


class LinkedList:
    def __init__(self):
        self.head: Optional[LinkedListNode] = None
        self.epsilon = 0.001
        self.count = 0.0
        self.max_value = -math.inf

    def update(self, lower_bound, upper_bound, value):
        self.count += 1

        if self.head is None:
            self.head = LinkedListNode(lower_bound, upper_bound, value)
            self.update_max_value(value)
            return

        # if self.check_change_head(lower_bound, upper_bound, value):
        #     return

        previous_node = None
        current_node = self.head

        inserted = False

        while current_node is not None:

            # Should be inserted before the current node
            if self.before_current_node(current_node, previous_node, lower_bound, upper_bound, value):
                return

            # Should be inserted after the current node
            after = self.after_current_node(current_node, previous_node, lower_bound)
            if after is not None:
                previous_node, current_node = after
                continue


            # There is an intersection

            # Same interval
            if self.same_interval(current_node, lower_bound, upper_bound, value):
                return

            # Find the intersection interval
            common_lower = max(lower_bound, current_node.lower_bound)
            common_upper = min(upper_bound, current_node.upper_bound)

            # Create a node with the intersection interval and update the value
            update_node = LinkedListNode(common_lower, common_upper, current_node.value)
            update_node.update_value(value)
            self.update_max_value(update_node.value)

            previous_node = self.part_before_intersection(current_node, previous_node, update_node, lower_bound, common_lower, value)

            x = self.part_after_intersection(current_node, update_node, upper_bound, common_upper, value)
            if x is not None:
                current_node, lower_bound, upper_bound, value = x
            else:
                return

        # should be inserted as the last node
        if not inserted:
            previous_node.next = LinkedListNode(lower_bound, upper_bound, value)
            self.update_max_value(value)

    def update_max_value(self, value_candidate):
        self.max_value = max(self.max_value, value_candidate)

    def value(self):
        return self.max_value / self.count

    def check_change_head(self, lower_bound, upper_bound, value):

        if self.before_current_node(self.head, None, lower_bound, upper_bound, value):
            return True

        if self.head.upper_bound < lower_bound:
            return False

        if self.same_interval(self.head, lower_bound, upper_bound, value):
            return True


        #TODO: not good
        # Find the intersection interval
        common_lower = max(lower_bound, self.head.lower_bound)
        common_upper = min(upper_bound, self.head.upper_bound)

        # Create a node with the intersection interval and update the value
        update_node = LinkedListNode(common_lower, common_upper, self.head.value)
        update_node.update_value(value)

        self.part_before_intersection(self.head, None, update_node, lower_bound, common_lower, value)

        x = self.part_after_intersection(self.head, update_node, upper_bound, common_upper, value)
        if x is not None:
            lower_bound, upper_bound, value = x  #TODO: need to return this somehow, this code is duplicate. maybe create a function
        else:
            return



    def before_current_node(self, current_node, previous_node, lower_bound, upper_bound, value):
        if current_node.lower_bound > upper_bound:
            new_node = LinkedListNode(lower_bound, upper_bound, value)
            new_node.next = current_node

            self.update_max_value(value)

            if current_node == self.head:
                self.head = new_node
            else:
                previous_node.next = new_node
            return True

        return False

    def after_current_node(self, current_node, previous_node, lower_bound):
        if current_node.upper_bound < lower_bound:
            previous_node = current_node
            current_node = current_node.next
            return previous_node, current_node

        return None

    def same_interval(self, current_node, lower_bound, upper_bound, value):
        if current_node.lower_bound == lower_bound and current_node.upper_bound == upper_bound:
            current_node.update_value(value)
            self.update_max_value(value)
            return True

        return False

    def part_before_intersection(self, current_node, previous_node, update_node, lower_bound, common_lower, value):
        if current_node.lower_bound < common_lower or lower_bound < common_lower:
            upper_bound = common_lower - self.epsilon

            if current_node.lower_bound < common_lower:
                first_node = LinkedListNode(current_node.lower_bound, upper_bound, current_node.value)
            else:
                first_node = LinkedListNode(lower_bound, upper_bound, value)
                self.update_max_value(value)

            if current_node == self.head:
                self.head = first_node
            else:
                previous_node.next = first_node
            first_node.next = update_node
            update_node.next = current_node.next

            # If there is a part after the intersection the nodes must be updated
            return first_node

        return previous_node


    def part_after_intersection(self, current_node, update_node, upper_bound, common_upper, value):
        lower_bound = common_upper + self.epsilon

        if current_node.upper_bound > common_upper:
            return update_node, lower_bound, current_node.upper_bound, current_node.value

        if upper_bound > common_upper:
            return update_node, lower_bound, upper_bound, value

        return None



