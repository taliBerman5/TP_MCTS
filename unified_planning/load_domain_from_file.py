import os

import dill
import unified_planning as up
import unified_planning.domains
from unified_planning.shortcuts import *

print(os.getcwd())
with open("../pickle_domains/stuck_car_domain_comb_1.pkl", "rb") as file:
    loaded_obj = dill.load(file)

