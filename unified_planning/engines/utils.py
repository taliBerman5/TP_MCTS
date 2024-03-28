import unified_planning as up
from typing import List
def create_init_stn(mdp: "up.engines.MDP"):
    """
    Creats
    :param mdp:
    :return:
    """
    stn = up.plans.stn.STNPlan([])

    if mdp.problem.deadline:  # Add the deadline to the STN
        deadline = mdp.problem.deadline
        stn.add_deadline(deadline)
    return stn



def update_stn(stn: "up.plans.stn.STNPlan", action: "up.engines.Action", previous_action_node: "up.plans.stn.STNPlanNode"=None, type=None):
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
    :param previous_action_node: the previous chosen action chosen
    :param action: according to the `action` constraints are added
    :return: The STNPlanNode of the `action`
    """

    if isinstance(action, up.engines.action.InstantaneousStartAction):
        start_node = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.START, up.plans.plan.ActionInstance(action, ()))
        if previous_action_node:
            stn.add_constrains_to_previous_chosen_action([(previous_action_node, 0, None, start_node)])
        else:
            stn.add_action(start_node)


        end_node = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.END,
                                              up.plans.plan.ActionInstance(action.end_action, ()))
        # Add constrains between the start and end action
        lower_bound = action.duration.lower.type.lower_bound
        upper_bound = action.duration.upper.type.upper_bound
        stn.add_potential_end_action([(start_node, lower_bound, upper_bound, end_node)])

        check_fix_time(stn, start_node, type)
        return start_node

    if isinstance(action, up.engines.action.InstantaneousEndAction):
        # Find the end node already created
        temp_end_node = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.END, up.plans.plan.ActionInstance(action, ()))
        end_potential = list(stn._potential_end_actions.keys())
        end_node = end_potential[end_potential.index(temp_end_node)]
        start_node = stn._potential_end_actions[end_node]


        stn.add_end_action_constrains([(start_node,end_node)])

        if start_node != previous_action_node:
            stn.add_constrains_to_previous_chosen_action([(previous_action_node, 0, None, end_node)])
        check_fix_time(stn, end_node, type)
        return end_node


    # InstantaneousAction
    Instant_node = up.plans.stn.STNPlanNode(up.model.timing.TimepointKind.START, up.plans.plan.ActionInstance(action, ()))
    if previous_action_node:
        stn.add_constrains_to_previous_chosen_action([(previous_action_node, 0, None, Instant_node)])
    else:
        stn.add_action(Instant_node)

    check_fix_time(stn, Instant_node, type)

    return Instant_node


def check_fix_time(stn: "up.plans.stn.STNPlan", action: "up.plans.stn.STNPlanNode", type):
    if type == 'SetTime':
        fix_time = stn.get_current_time(action)
        stn.fix_action_time(action, fix_time)