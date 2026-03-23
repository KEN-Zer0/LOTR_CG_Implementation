# 0 - sensitivty analysis
# 1 - single RL run
# 2 - RL direct optimization
# 3 - mcts trial
# 4 - RL AC macro optimization
# 5 - RLQ macro optimization
pipeline = 5
num_episodes = 10000
############################# RL ########################
# 0 - enemies + round
# 1 - enemies + lands + round
# 2 - enemies + combined threat
# 3 - combined threat + enemies engaged
encoding = 0
default_lr = 0.0002
n_neurons = 50
rlMode = 'llrlr'

############################# mcts #######################
mctsMode = 'rmrmr'
playoutBudget = 600
playoutsPerSimulation = 30
playoutType = 0 ## 0 - random, 1 - expert
reduction_planning = True
reduction_questing = True
reduction_defense = True

########################## game model ####################
difficulty = 'easy'
fullGame = False
