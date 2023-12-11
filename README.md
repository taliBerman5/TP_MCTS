# TP-MCTS (Temporal Planning Monte Carlo Tree Search)

TP-MCTS algorithm combines the well-known Monte Carlo Tree Search (MCTS) algorithm (Coulom 2006) with ideas from classical temporal
planning. Specifically, the nodes of the tree developed by
TP-MCTS contains both a state and a Simple Temporal Network (STN) (Dechter, Meiri, and Pearl 1991), which represents the various temporal constraints the plan must satisfy
and comes with efficient consistency checking and solution generation algorithms.
