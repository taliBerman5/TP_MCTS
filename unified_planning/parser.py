import argparse

parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('-d', '--deadline', help='deadline of the problem', nargs='?', default=None, type=int)
parser.add_argument('-st', '--search_time', help='amount of time in each step', nargs='?', default=10, type=int)
parser.add_argument('-sd', '--search_depth', help='search depth of ', nargs='?', default=40, type=int)
parser.add_argument('-se', '--selection_type', help='selection type in MCTS algorithm', nargs='?', default='avg')
parser.add_argument('-r', '--runs', help='how many runs to run the script', nargs='?', default=1, type=int)
parser.add_argument('-dt', '--domain_type', help='combination, new approach or new approach same as the baseline', nargs='?', default='regular')
parser.add_argument('-s', '--solver', help='solver', nargs='?', default='mcts')
parser.add_argument('-do', '--domain', help='domain')
parser.add_argument('-e', '--exploration_constant', help='the exploration constant for mcts solver', nargs='?', default=10, type=int)
parser.add_argument('-ge', '--garbage_amount', help='how many garbage actions to add to the domain', nargs='?', default=10, type=int)

args = parser.parse_args()