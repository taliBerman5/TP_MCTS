from typing import Optional
import math

from unified_planning.engines import node


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

    def max_update_value(self, reward):
        self.value = max(self.value, reward)

    def interval(self):
        return self.lower_bound, self.upper_bound

    def update_df_reward(self, discount_factor, reward):
        self.value = self.value * discount_factor + reward
        current_node = self.next
        while current_node is not None:
            current_node.value = current_node.value * discount_factor + reward
            current_node = current_node.next

    def get_max_value_interval(self):
        max = self.value
        lower, upper = self.interval()

        current_node = self.next

        while current_node is not None:
            if current_node.value > max:
                max = current_node.value
                lower, upper = current_node.interval()
            current_node = current_node.next

        return max, lower, upper


class LinkedList:
    def __init__(self):
        self.head: Optional[LinkedListNode] = None
        self.epsilon = 0.001
        self.max_value = -math.inf
        self.max_interval = (0, math.inf)

    def interval_value(self, lower, upper):
        """ Returns the value of the intervals between the lower and upper bound

        returns:  node -
                  The sub_intervals of the interval between the lower and upper bound with corresponding values
        """

        if self.head is None:
            return None

        current_node = self.head
        node = None

        while current_node is not None and lower <= upper:

            if current_node.lower_bound > upper:
                return node

            if lower > current_node.upper_bound:
                current_node = current_node.next

            else:

                common_lower = max(lower, current_node.lower_bound)
                common_upper = min(upper, current_node.upper_bound)

                if node is None:
                    node = LinkedListNode(common_lower, common_upper, current_node.value)
                else:
                    node.next = LinkedListNode(common_lower, common_upper, current_node.value)

                lower = current_node.upper_bound + self.epsilon

        return node

    def insert(self, node):
        if self.head is None:
            self.head = node

        current_node = self.head
        while current_node.next is not None:
            current_node = current_node.next

        current_node.next = node

    def update(self, add_node: LinkedListNode, type="AVG"):
        """updates the value of the list according to the add_node intervals
        param add_node: node to update
        param type: type of update (AVG, Max)

        returns:  updated node with the updated value

        """
        if self.head is None:
            self.head = add_node
            self.update_max_value(*add_node.get_max_value_interval())
            return add_node

        previous_node = None
        current_node = self.head
        update_list = LinkedList()

        while current_node is not None and add_node is not None:

            # Should be inserted before the current node
            if self.before_current_node(current_node, previous_node, add_node.lower_bound, add_node.upper_bound, add_node.value):
                update_list.insert(LinkedListNode(add_node.lower_bound, add_node.upper_bound, add_node.value))
                add_node = add_node.next
                continue

            # Should be inserted after the current node
            after = self.after_current_node(current_node, add_node.lower_bound)
            if after is not None: # Should insert after the current node
                previous_node, current_node = after
                continue

            # There is an intersection

            # Same interval
            if self.same_interval(current_node, add_node.lower_bound, add_node.upper_bound, add_node.value):
                update_list.insert(LinkedListNode(add_node.lower_bound, add_node.upper_bound, current_node.value))
                add_node = add_node.next
                continue

            # Find the intersection interval
            common_lower = max(add_node.lower_bound, current_node.lower_bound)
            common_upper = min(add_node.upper_bound, current_node.upper_bound)

            # Create a node with the intersection interval and update the value
            common_node = LinkedListNode(common_lower, common_upper, current_node.value)
            if type == 'AVG':
                common_node.update_value(add_node.value)
            else:
                common_node.max_update_value(add_node.value)

            self.update_max_value(common_node.value, common_lower, common_upper)

            previous_node = self.part_before_intersection(current_node, previous_node, common_node, update_list, add_node.lower_bound,
                                                          common_lower, add_node.value)

            update_list.insert(common_node)

            current_node, add_node = self.part_after_intersection(current_node, previous_node, add_node, common_upper)

        # should be inserted as the last node
        if add_node is not None:
            previous_node.next = add_node
            self.update_max_value(*add_node.get_max_value_interval())

        return update_list.head

    def update_max_value(self, value_candidate, lower_bound, upper_bound):
        if self.max_value < value_candidate:
            self.max_value = value_candidate
            self.max_interval = lower_bound, upper_bound

    def before_current_node(self, current_node, previous_node, lower_bound, upper_bound, value):
        if current_node.lower_bound > upper_bound:
            new_node = LinkedListNode(lower_bound, upper_bound, value)
            new_node.next = current_node

            self.update_max_value(value, lower_bound, upper_bound)

            if current_node == self.head:
                self.head = new_node
            else:
                previous_node.next = new_node
            return True

        return False

    def after_current_node(self, current_node, lower_bound):
        if current_node.upper_bound < lower_bound:
            previous_node = current_node
            current_node = current_node.next
            return previous_node, current_node

        return None

    def same_interval(self, current_node, lower_bound, upper_bound, value):
        if current_node.lower_bound == lower_bound and current_node.upper_bound == upper_bound:
            current_node.update_value(value)
            self.update_max_value(value, lower_bound, upper_bound)
            return True

        return False

    def part_before_intersection(self, current_node, previous_node, common_node, update_list, lower_bound, common_lower, value):

        if current_node.lower_bound < common_lower or lower_bound < common_lower:
            upper_bound = common_lower - self.epsilon

            if current_node.lower_bound < common_lower:
                first_node = LinkedListNode(current_node.lower_bound, upper_bound, current_node.value)
            else:
                first_node = LinkedListNode(lower_bound, upper_bound, value)
                self.update_max_value(value, lower_bound, upper_bound)

                update_list.insert(first_node)

            first_node.next = common_node

        else:  # lower_bound = current_node.lower_bound
            first_node = common_node


        if current_node == self.head:
            self.head = first_node
        else:
            previous_node.next = first_node

        common_node.next = current_node.next

        # If there is a part after the intersection the nodes must be updated
        return first_node



    def part_after_intersection(self, current_node, previous_node, add_node, common_upper):
        lower_bound = common_upper + self.epsilon

        if current_node.upper_bound > common_upper:
            next = previous_node.next
            current_node = LinkedListNode(lower_bound, current_node.upper_bound, current_node.value)
            previous_node.next = current_node
            current_node.next = next
            return current_node, add_node.next

        if add_node.upper_bound > common_upper:
            add_node.lower_bound = lower_bound
            return previous_node.next, add_node

        return previous_node, add_node.next
