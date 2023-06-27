
from typing import Dict, Optional, Set
import unified_planning as up
from unified_planning.exceptions import UPUsageError, UPValueError



class ROState:
    """This is an abstract class representing a classical `Read Only state`"""

    def get_value(self, value: "unified_planning.model.FNode") -> "unified_planning.model.FNode":
        """
        This method retrieves the value in the state.
        NOTE that the searched value must be set in the state.

        :param value: The value searched for in the state.
        :return: The set value.
        """
        raise NotImplementedError

    def predicates(self) -> Set["up.model.fnode.Fnode"]:
        """
         This method returns the predicates of the state

        :return: The predicates
        """

        raise NotImplementedError