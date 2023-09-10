import math
import statistics


def evaluation_loop(runs, plan_func, params):
    amount_success = 0
    time_round = []
    avg_time = -math.inf
    std_time = -1

    for i in range(runs):
        print(f'Started round {i}')
        success, time = plan_func(*params)
        amount_success += success
        if time > -math.inf:
            time_round.append(time)

    if len(time_round) > 0:
        avg_time = statistics.mean(time_round)
    if len(time_round) > 1:
        std_time = statistics.stdev(time_round) / math.sqrt(amount_success)

    print(f'Completed = {runs}')
    print(f'Amount of success = {amount_success}')
    print(f'Average success time = {avg_time}')
    print(f'STD success time = {std_time}')
    return amount_success, avg_time, std_time
