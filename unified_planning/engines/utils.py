import unified_planning as up
from typing import List
def create_init_stn(mdp: "up.engines.MDP"):
    """
    Creats
    :param mdp:
    :return:
    """
    deadline = None
    start_plan = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.GLOBAL_START)
    end_plan = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.GLOBAL_END)

    if mdp.problem.deadline:
        deadline = mdp.problem.deadline.lower.delay
    stn = up.plans.stn.STNPlan([(start_plan, None, deadline, end_plan)])  # Add the deadline to the STN
    return stn



def update_stn(stn: "up.plans.stn.STNPlan", action: "up.engines.Action", previous_action: "up.plans.stn.STNPlanNode"=None):
    """
    Add constrains to the `stn` according to the `action` and the `previous_action`

    if the previous_action is not None
     - a constraint between the `previous_action` and the `action` is added

    if the `action` is  InstantaneousStartAction or InstantaneousAction:
     - add the action to the stn if the previous_action is None

     if the `action` is  InstantaneousStartAction
     - add a potential constraint to the end action

     if the `action` is  InstantaneousEndAction
     - add a constraint to the start action


    :param stn: The STN containing the constraints so far
    :param previous_action: the previous chosen action chosen
    :param action: according to the `action` constraints are added
    :return: The STNPlanNode of the `action`
    """
    if isinstance(action, up.engines.action.InstantaneousStartAction):
        start_node = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.START, up.plans.plan.ActionInstance(action, ()))
        if previous_action:
            stn.add_constrains([(previous_action, 0, None, start_node)])
        else:
            stn.add_action(start_node)


        end_node = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.END,
                                              up.plans.plan.ActionInstance(action.end_action, ()))
        # Add constrains between the start and end action
        lower_bound = action.duration.lower.type.lower_bound
        upper_bound = action.duration.upper.type.upper_bound
        stn.add_potential_end_action([(start_node, lower_bound, upper_bound, end_node)])

        return start_node

    if isinstance(action, up.engines.action.InstantaneousEndAction):
        end_node = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.END, up.plans.plan.ActionInstance(action, ()))
        start_node = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.START,
                                              up.plans.plan.ActionInstance(action.start_action, ()))

        assert previous_action  # The start action should already be in the history

        # Add constrains between the start and end action
        lower_bound = action.start_action.duration.lower.type.lower_bound
        upper_bound = action.start_action.duration.upper.type.upper_bound
        stn.add_constrains([(start_node, lower_bound, upper_bound, end_node)])

        if start_node != previous_action:
            stn.add_constrains([(previous_action, 0, None, end_node)])

        return end_node


    # InstantaneousAction
    start_node = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.START, up.plans.plan.ActionInstance(action, ()))
    if previous_action:
        stn.add_constrains([(previous_action, 0, None, start_node)])
    else:
        stn.add_action(start_node)
