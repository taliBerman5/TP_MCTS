
from typing import Deque, Dict, List, Optional, Any, Generic, Set, Tuple, TypeVar, cast
class LinkedListNode:
    def __init__(self, lower_bound, upper_bound, value, count = 1):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.value = value
        self.count = count
        self.next: Optional["LinkedListNode"] = None


    def update_value(self, reward, count):
        self.value = (self.value * self.count + reward * count) / (self.count + count)
        self.count += count


class LinkedList:
    def __init__(self):
        self.head: Optional[LinkedListNode] = None
        self.epsilon = 0.001
    def update(self, lower_bound, upper_bound, value):
        if self.head is None:
            self.head = LinkedListNode(lower_bound, upper_bound, value)

        else:

            if self.check_change_head(lower_bound, upper_bound, value):
                return

            previous_node = self.head
            current_node = self.head.next

            inserted = False
            count = 1

            while current_node is not None:
                # Should be inserted before the current node
                if current_node.lower_bound > upper_bound:
                    new_node = LinkedListNode(lower_bound, upper_bound, value)
                    new_node.next = current_node
                    previous_node.next = new_node
                    inserted = True
                    break

                # Should be inserted after the current node
                if current_node.upper_bound < lower_bound:
                    previous_node = current_node
                    current_node = current_node.next
                    continue

                # There is an intersection

                # Same interval
                if current_node.lower_bound == lower_bound and current_node.lower_bound == upper_bound:
                    update_node = LinkedListNode(lower_bound, lower_bound, current_node.value, current_node.count)
                    update_node.update_value(value, count)
                    inserted = True
                    break


                # Find the intersection interval
                common_lower = max(lower_bound, current_node.lower_bound)
                common_upper = min(upper_bound, current_node.upper_bound)

                # Create a node with the intersection interval and update the value and count
                update_node = LinkedListNode(common_lower, common_upper, current_node.value, current_node.count)
                update_node.update_value(value, count)


                # Both lower bound is the same
                if current_node.lower_bound == lower_bound:
                    previous_node.next = update_node
                    update_node.next = current_node.next

                    previous_node = update_node
                    lower_bound = common_upper + self.epsilon

                    if current_node.upper_bound > common_upper:
                        upper_bound = current_node.upper_bound
                        count = current_node.count

                # Both upper bounds is the same
                if current_node.upper_bound == upper_bound:
                    update_node.next = current_node.next

                    if current_node.lower_bound < lower_bound:
                        new_node = LinkedListNode(current_node.lower_bound, common_lower - self.epsilon,
                                                  current_node.value, current_node.count)
                    else:
                        new_node = LinkedListNode(lower_bound, common_lower - self.epsilon, value, count)

                    previous_node.next = new_node
                    new_node.next = update_node
                    inserted = True
                    break

                # There is a part of the before the intersection
                else:

                    # part of current node interval is before of the intersection
                    if current_node.lower_bound < common_lower:
                        new_node = LinkedListNode(current_node.lower_bound, common_lower - self.epsilon, current_node.value, current_node.count)

                    # part of inserted node interval is before of the intersection
                    else:
                        new_node = LinkedListNode(lower_bound, common_lower - self.epsilon, value,
                                                  count)

                    previous_node.next = new_node
                    new_node.next = update_node
                    update_node.next = current_node.next

                    # There is an interval after the intersection to be inserted
                    # For example current [3-6] and new interval [4-5]
                    lower_bound = common_upper + self.epsilon
                    if current_node.upper_bound > common_upper:
                        upper_bound = current_node.upper_bound
                        count = current_node.count



            # should be inserted as the last node
            if not inserted:
                previous_node.next = LinkedListNode(lower_bound, upper_bound, value)



    def check_change_head(self, lower_bound, upper_bound, value):
        if self.head.lower_bound > upper_bound:
            new_head = LinkedListNode(lower_bound, upper_bound, value)
            new_head.next = self.head
            self.head = new_head  #TODO: check if works correctly


        if self.head.lower_bound > lower_bound:
            if self.head.upper_bound > upper_bound:

