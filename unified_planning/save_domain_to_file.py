import os
import sys

"""For the bash script"""
# Get the current directory (where the script is located)

current_directory = os.path.dirname(os.path.abspath(__file__))
print(current_directory)

# Get the parent directory
parent_directory = os.path.dirname(current_directory)
print(parent_directory)
sys.path.append(parent_directory)  # Add the path to your 'unified_planning' directory


import unified_planning as up
import unified_planning.domains
from unified_planning.shortcuts import *
import dill



def create_save_model(file_name, domain, object_amount=1, garbage_amount=0):
    model = domain(kind='combination', deadline=up.args.deadline, object_amount=object_amount, garbage_amount=garbage_amount)

    if domain == up.domains.Nasa_Rover:
        grounder = up.engines.compilers.Grounder(model.grounding_map())
    else:
        grounder = up.engines.compilers.Grounder()
    grounding_result = grounder._compile(model.problem)
    ground_problem = grounding_result.problem

    convert_combination_problem = Convert_problem_combination(ground_problem)
    converted_problem = convert_combination_problem._converted_problem
    model.remove_actions(converted_problem)

    with open(file_name, "wb") as file:
        dill.dump(convert_combination_problem, file)


# create_save_model("../pickle_domains/stuck_car_domain_comb.pkl", up.domains.Stuck_Car)
# create_save_model("../pickle_domains/machine_shop_domain_comb.pkl", up.domains.Machine_Shop)
# # create_save_model("../pickle_domains/nasa_rover_domain_comb_1.pkl", up.domains.Nasa_Rover)
# create_save_model("../pickle_domains/strips_domain_comb.pkl", up.domains.Strips)
# create_save_model("../pickle_domains/full_strips_domain_comb.pkl", up.domains.Full_Strips)

# for o in range(2, 4):
#     nasa_rover = up.domains.Nasa_Rover
#     create_save_model(f"../pickle_domains/nasa_rover_domain_comb_{o}.pkl", nasa_rover, object_amount=o)


for o in range(3, 5):
    machine_shop = up.domains.Machine_Shop
    create_save_model(f"../pickle_domains/machine_shop_domain_comb_{o}.pkl", machine_shop, object_amount=o)

# for g in range(11):
#     strips_prob = up.domains.Strips_Prob
#     create_save_model(f"../pickle_domains/strips_prob_domain_comb_{g}.pkl", strips_prob, garbage_amount=g)
#
#
# for g in range(5, 30):
#     simple = up.domains.Simple
#     create_save_model(f"../pickle_domains/simple_domain_comb_{g}.pkl", simple, garbage_amount=g)
