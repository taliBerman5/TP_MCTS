# TP-MCTS (Temporal Planning Monte Carlo Tree Search)

TP-MCTS algorithm combines the well-known Monte Carlo Tree Search (MCTS) algorithm (Coulom 2006) with ideas from classical temporal
planning. Specifically, the nodes of the tree developed by
TP-MCTS contains both a state and a Simple Temporal Network (STN) (Dechter, Meiri, and Pearl 1991), which represents the various temporal constraints the plan must satisfy
and comes with efficient consistency checking and solution generation algorithms.

## domains

* **Stuck Car(C)** - C cars are stuck in the mud. The goal of the C agents is to get the cars out of the mud before a deadline is reached.
* **Nasa Rover(R)** - A probabilistic variant of the well-known NASA Rover domain from the 2002 AIPS Planning Competition (Long and Fox 2003a) with R different rovers.
* **Machine Shop(O)** - This domain captures a manufacturing environment comprising various subtasks, including shaping, painting, polishing, and more.
* **Simple-x** - In this simple domain, there are x distinct actions, each of which accomplishes a unique goal upon completion.
* **Conc** - This domain was designed to challenge the planners’ abilities to handle problems requiring maximal concurrency to meet a deadline.
* **Prob Conc+G** - A probabilistic version of the Conc domain.

## Quick Start

To Run an experiment use the bash file runexp:

```bash
$ cd TP_MCTS
$ bash runexp -l log/nasa_rover.log run_domain.py --domain nasa_rover --deadline 35 --runs 3 
```

This command computes the TP-MCTS algorithm on the Nasa Rover(1) domain with a deadline of 35 seconds `N = 3` runs and outputs the results to nasa_rover.log file. 

For more usage parameters see "[usage parameters](doc/usage_parameters.txt)".

