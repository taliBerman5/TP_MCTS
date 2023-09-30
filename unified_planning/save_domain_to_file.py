import unified_planning as up
import unified_planning.domains
from unified_planning.shortcuts import *
import dill


def create_save_model(file_name, domain, garbage_amount=0):
    model = domain(kind='combination', deadline=up.args.deadline, garbage_amount=garbage_amount)
    grounder = up.engines.compilers.Grounder()
    grounding_result = grounder._compile(model.problem)
    ground_problem = grounding_result.problem

    convert_combination_problem = Convert_problem_combination(ground_problem)
    converted_problem = convert_combination_problem._converted_problem
    model.remove_actions(converted_problem)

    with open(file_name, "wb") as file:
        dill.dump(convert_combination_problem, file)


create_save_model("../pickle_domains/stuck_car_domain_comb.pkl", up.domains.Stuck_Car)
create_save_model("../pickle_domains/machine_shop_domain_comb.pkl", up.domains.Machine_Shop)
create_save_model("../pickle_domains/nasa_rover_domain_comb.pkl", up.domains.Nasa_Rover)
create_save_model("../pickle_domains/strips_domain_comb.pkl", up.domains.Strips)
create_save_model("../pickle_domains/full_strips_domain_comb.pkl", up.domains.Full_Strips)

for g in range(11):
    strips_prob = up.domains.Strips_Prob
    create_save_model(f"strips_prob_domain_comb_{g}.pkl", strips_prob, garbage_amount=g)
