from typing import Optional
import math

from unified_planning.engines import node


class LinkedListNode:
    def __init__(self, lower_bound, upper_bound, value):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.value = value
        self.next: Optional["LinkedListNode"] = None

    def equal(self, oth: object) -> bool:
        if isinstance(oth, LinkedListNode):
            if self.lower_bound == oth.lower_bound and \
                    self.upper_bound == oth.upper_bound and self.value == oth.value:
                if self.next is None:
                    return True
                else:
                    return self.next.equal(oth.next)
        else:
            return False

    def copy(self):
        copy = LinkedListNode(self.lower_bound, self.upper_bound, self.value)
        if self.next is not None:
            copy.next = self.next.copy()
        return copy

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

    def divide_count_reward(self, count):
        self.value = self.value / count
        current_node = self.next
        while current_node is not None:
            current_node.value = current_node.value / count
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
        self._max_value = -math.inf
        self._max_interval = (0, math.inf)

    @property
    def max_value(self):
        return self._max_value

    @property
    def max_interval(self):
        return self._max_interval

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

    def update(self, lower_bound, upper_bound, value):
        """updates the value of the list according to the lower_bound and upper_bound
        param lower_bound: lower bound of the interval to update
        param upper_bound: upper bound of the interval to update
        param value: the value to update the interval with

        """
        if self.head is None:
            self.head = LinkedListNode(lower_bound, upper_bound, value)
            self.update_max_value(lower_bound, upper_bound, value)
            return

        previous_node = None
        current_node = self.head

        while current_node is not None:

            # Should be inserted before the current node
            if self.before_current_node(current_node, previous_node, lower_bound, upper_bound,
                                        value):
                return

            # Should be inserted after the current node
            after = self.after_current_node(current_node, lower_bound)
            if after is not None:  # Should insert after the current node
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
            common_node = LinkedListNode(common_lower, common_upper, current_node.value)
            common_node.update_value(value)

            self.update_max_value(common_lower, common_upper, common_node.value)

            previous_node = self.part_before_intersection(current_node, previous_node, common_node,
                                                          lower_bound,
                                                          common_lower, value)

            x = self.part_after_intersection(current_node, previous_node, common_upper, upper_bound)
            if x is not None:
                current_node, lower_bound = x
            else:
                return

        # should be inserted as the last node
        previous_node.next = LinkedListNode(lower_bound, upper_bound, value)
        self.update_max_value(lower_bound, upper_bound, value)

    def update_max_value(self, lower_bound, upper_bound, value_candidate):
        """
        Works only  if the rewards are not negative
        update the max_value according to the added interval
        """

        # The candidate it bigger -> need to change
        if self.max_value < value_candidate:
            self._max_value = value_candidate
            self._max_interval = lower_bound, upper_bound
            return


    def before_current_node(self, current_node, previous_node, lower_bound, upper_bound, value):
        if current_node.lower_bound > upper_bound:
            new_node = LinkedListNode(lower_bound, upper_bound, value)
            new_node.next = current_node

            self.update_max_value(lower_bound, upper_bound, value)

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
            self.update_max_value(lower_bound, upper_bound, current_node.value)
            return True

        return False

    def part_before_intersection(self, current_node, previous_node, common_node, lower_bound, common_lower,
                                 value):

        if current_node.lower_bound < common_lower or lower_bound < common_lower:
            upper_bound = common_lower - self.epsilon

            if current_node.lower_bound < common_lower:
                first_node = LinkedListNode(current_node.lower_bound, upper_bound, current_node.value)
            else:
                first_node = LinkedListNode(lower_bound, upper_bound, value)

            first_node.next = common_node

        else:  # lower_bound = current_node.lower_bound
            first_node = common_node

        if current_node == self.head:
            self.head = first_node
        else:
            previous_node.next = first_node

        common_node.next = current_node.next

        # If there is a part after the intersection the nodes must be updated
        return common_node

    def part_after_intersection(self, current_node, previous_node, common_upper, upper_bound):
        lower_bound = common_upper + self.epsilon

        if current_node.upper_bound > common_upper:
            next = previous_node.next
            current_node = LinkedListNode(lower_bound, current_node.upper_bound, current_node.value)
            previous_node.next = current_node
            current_node.next = next
            return None

        if upper_bound > common_upper:
            return previous_node.next, lower_bound

        return None
