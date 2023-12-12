import os
import sys
import time

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



def create_save_model(domain_name, file_name, domain, object_amount=1, garbage_amount=0):
    start_time = time.time()
    model = domain(kind='combination', deadline=up.args.deadline, object_amount=object_amount, garbage_amount=garbage_amount)

    if domain == up.domains.Nasa_Rover:
        grounder = up.engines.compilers.Grounder(model.grounding_map())
    else:
        grounder = up.engines.compilers.Grounder()
    grounding_result = grounder._compile(model.problem)
    ground_problem = grounding_result.problem

    convert_combination_problem = Convert_problem_combination(model, ground_problem)
    converted_problem = convert_combination_problem._converted_problem
    model.remove_actions(converted_problem)

    end_time = time.time()

    elapsed_time = end_time - start_time

    # Print the result and elapsed time
    print(f"Compilation Time {domain_name} object={object_amount}, garbage={garbage_amount}: {elapsed_time} seconds")


    with open(file_name, "wb") as file:
        dill.dump(convert_combination_problem, file)


def compilation_time(domain_name, domain, object_amount=1, garbage_amount=0):
    start_time = time.time()
    model = domain(kind='combination', deadline=up.args.deadline, object_amount=object_amount, garbage_amount=garbage_amount)

    if domain == up.domains.Nasa_Rover:
        grounder = up.engines.compilers.Grounder(model.grounding_map())
    else:
        grounder = up.engines.compilers.Grounder()
    grounding_result = grounder._compile(model.problem)
    ground_problem = grounding_result.problem

    convert_combination_problem = Convert_problem_combination(model, ground_problem)
    converted_problem = convert_combination_problem._converted_problem
    model.remove_actions(converted_problem)

    end_time = time.time()

    elapsed_time = end_time - start_time

    # Print the result and elapsed time
    print(f"Compilation Time {domain_name} object={object_amount}, garbage={garbage_amount}: {elapsed_time} seconds")


# create_save_model("stuck_car_1o", "../pickle_domains/stuck_car_1o_domain_comb.pkl", up.domains.Stuck_Car_1o)
# create_save_model("conc", "../pickle_domains/conc_domain_comb.pkl", up.domains.Conc)
# create_save_model("full_conc", "../pickle_domains/full_conc_domain_comb.pkl", up.domains.Full_Conc)


for o in range(1, 4):
    stuck_car = up.domains.Stuck_Car
    create_save_model("stuck_car", f"../pickle_domains/stuck_car_domain_comb_{o}.pkl", stuck_car, object_amount=o)


# for o in range(2, 4):
#     nasa_rover = up.domains.Nasa_Rover
#     create_save_model("nasa_rover", f"../pickle_domains/nasa_rover_domain_comb_{o}.pkl", nasa_rover, object_amount=o)


# for g in range(11):
#     prob_conc = up.domains.Prob_Conc
#     create_save_model("prob_conc", f"../pickle_domains/prob_conc_domain_comb_{g}.pkl", prob_conc, garbage_amount=g)


# for g in range(5, 30):
#     simple = up.domains.Simple
#     create_save_model("simple", f"../pickle_domains/simple_domain_comb_{g}.pkl", simple, garbage_amount=g)
