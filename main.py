from os import pipe
import json
import simulators
# from Game_Model.game import Game
from defaultAgent import DefaultAgent
import Game_Model.globals
# from envs.lowLevelEnv import LowLevelEnv
# from vanilla_AC.agent import Agent
from vanilla_mcts.mctsAgent import MCTSAgent
from mainConfig import pipeline, num_episodes, n_neurons, rlMode, mctsMode, playoutBudget, playoutsPerSimulation, playoutType
import numpy as np
import time
import matplotlib.pyplot as plt
from itertools import product
import multiprocessing as mp
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
from hyperopt import tpe, hp, fmin

from simulators.lowLevelSimulator import LowLevelSimulator
from simulators.macroSimulator import MacroSimulator

Game_Model.globals.init() ###### uncomment!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# best_avg = -1

def sensitivityAnalysis(num_episodes):
    # for mode in product('re', repeat=5):
    #     agent = DefaultAgent(mode, num_episodes)
    #     rewards = agent.simulate()
    #     countWins(mode, rewards)
    
    agent = DefaultAgent('rrrrr', num_episodes)
    rewards = agent.simulate()
    success, failHeroes, failThreat = agent.getEpisodeLengths()
    saveEpisodesTotxt(success, failHeroes, failThreat)
    probs = agent.getDecisionProbs()
    print(probs)
    countWins(mctsMode, rewards)


########################################################################

def mctsTrialNuevo(params):
    Game_Model.globals.init()
    mcts = MCTSAgent(params[0], params[1], params[2], params[3])
    return mcts.simulate()

########################################################################
    
def mctsTrial(params):
    mcts = MCTSAgent(params[0], params[1], params[2], params[3])
    return mcts.simulate()

def mctsPlayoutbudget():
    # budgets = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    budgets = list(range(1,10)) + list(range(10, 110, 10))
    for budget in budgets:    
        params = []
        for _ in range(1000):
            params.append([mctsMode, budget, playoutsPerSimulation, playoutType])
        p = mp.Pool()
        rewards = []
        for reward, _, _ in p.map(mctsTrialNuevo, params):
            rewards.append(reward)
        print(f'Budget: {budget}:')
        countWins(mctsMode, rewards)

def mctsPlayoutPerSimulation():
    ppsims = range(10, 110, 10)
    for ppsim in ppsims:    
        params = []
        for _ in range(1000):
            params.append([mctsMode, playoutBudget, ppsim, playoutType])
        p = mp.Pool()
        rewards = []
        for reward, _, _ in p.map(mctsTrialNuevo, params):
            rewards.append(reward)
        print(f'Playouts Per Simulation: {ppsim}:')
        countWins(mctsMode, rewards)

def mctsSingleTest(num_episodes):
    params = []
    for _ in range(num_episodes):
        params.append([mctsMode, playoutBudget, playoutsPerSimulation, playoutType])
    p = mp.Pool()
    rewards = []
    successEpisodes = []
    failEpisodes = []
    for reward, success, fail in p.map(mctsTrialNuevo, params):
        rewards.append(reward)
        successEpisodes.append(success)
        failEpisodes.append(fail)

    successEpisodes = [su + 1 for su in successEpisodes if su]
    failEpisodes = [fa + 1 for fa in failEpisodes if fa]
    np.savetxt(mctsMode + '_successEpisodes.txt', successEpisodes, fmt='%d', newline=' ')
    np.savetxt(mctsMode + '_failEpisodes.txt', failEpisodes, fmt='%d', newline=' ')

    print(f'Budget: {playoutBudget}:')

    countWins(mctsMode, rewards)

def mctsTimeMeasure(num_ep):
    params = [mctsMode, playoutBudget, playoutsPerSimulation, playoutType]
    rewards = []
    successEpisodes = []
    failEpisodes = []
    start = time.time()
    for _ in range(num_ep):
        reward, _, _ = mctsTrialNuevo(params)
        rewards.append(reward)
    end = time.time()
    print(f'Budget: {playoutBudget}:')
    countWins(mctsMode, rewards)
    print(f'execution time of one episode: {(end - start) / num_ep} sec')

def countWins(mode, rewards):
    total = 0
    score = 0
    for digit in rewards:
        total += 1
        if digit:
            score += 1
    winrate = score / total * 100
    z = 1.96 # for 95% confidence level
    interv = z * np.sqrt(winrate * (100 - winrate) / total)
    print(f'{mode} winrate: {winrate} ({np.around(interv, decimals=2)})')

def saveEpisodesTotxt(success, failHeroes, failThreat):
    np.savetxt('rrrrr_successEpisodes.txt', success, fmt='%d', newline=' ')
    np.savetxt('rrrrr_failHeroes.txt', failHeroes, fmt='%d', newline=' ')
    np.savetxt('rrrrr_failThreat.txt', failThreat, fmt='%d', newline=' ')

def plotScoreHistory(score_history):
    x = np.arange(100, num_episodes + 1)
    moving_avg = np.convolve(score_history, np.ones(100), 'valid') / 100
    plt.plot(x, moving_avg)
    plt.xlabel('episode')
    plt.ylabel('winrate')
    plt.show()

def plotScoreHistoryFromFile():
    x = np.arange(100, num_episodes + 1)
    x1 = np.arange(1000, num_episodes + 1)
    score_history = np.loadtxt('score_history.txt')
    moving_avg = np.convolve(score_history, np.ones(100), 'valid') / 100
    moving_avg1 = np.convolve(score_history, np.ones(1000), 'valid') / 1000
    plt.plot(x, moving_avg)
    plt.plot(x1, moving_avg1)
    plt.xlabel('episode')
    plt.ylabel('avg_score')
    figName = 'p' + str(pipeline) + 'nn' + str(n_neurons) +'.png'
    plt.savefig(figName)

def main():
    if pipeline == 0:
        sensitivityAnalysis(num_episodes)
    elif pipeline == 1:
        encoding = 1
        space = { 'lrp': 4.5e-4,
            'lrq': 8e-4,
            'n_neurons_p': 150,
            'n_neurons_q': 120,
        }
        simulator = LowLevelSimulator(encoding)
        avg_score, score_history = simulator.objective(space)
        np.savetxt('score_history.txt', score_history, fmt='%f', newline=' ')
        plotScoreHistory(score_history)
    elif pipeline == 2:
        encodings = [2]
        for en in encodings:
            simulator = LowLevelSimulator(en)
            space = {
		        ### best rlrrr ###
		        'lrq': hp.choice('lrq', [0.00065]),
		        'n_neurons_q': hp.choice('n_neurons_q', [110])
                ### best llrrr ###
                # 'lrp': hp.choice('lrp', [0.00045]),
                # 'lrq': hp.choice('lrq', [0.0008]),
                # 'n_neurons_p': hp.choice('n_neurons_p', [150]),
                # 'n_neurons_q': hp.choice('n_neurons_q', [120])
                ################################
                # 'lr': hp.loguniform('lrp', -9, -7),
                # 'lrp': hp.choice('lrp', [3e-4, 3.5e-4, 4e-4, 4.5e-4, 5e-4, 5.5e-4]),
                # 'lrq': hp.choice('lrq', [6e-4, 6.5e-4, 7e-4, 7.5e-4, 8e-4, 8.5e-4, 9e-4, 1e-3]),
                # 'lrd': hp.choice('lrd', [1e-4, 2e-4, 3e-4, 4e-4, 5e-4, 6e-4, 7e-4]),
                # 'n_neurons_p': hp.choice('n_neurons_p', [100, 110, 120, 130, 140, 150, 160]),
                # 'n_neurons_q': hp.choice('n_neurons_q', [100, 110, 120, 130, 140])
                # 'n_neurons_q': hp.choice('n_neurons_q', [80, 90, 100, 110, 120, 130, 140, 150])
                # 'n_neurons_d': hp.choice('n_neurons_d', [50, 60, 70, 80, 90, 100])
            }
            best = fmin(
                fn=simulator.objective,
                space=space,
                algo=tpe.suggest,
                max_evals=1
            )
            print(best)
    elif pipeline == 3:
        # mctsPlayoutbudget()
        # mctsPlayoutPerSimulation()
        # mctsSingleTest(1000)
        mctsTimeMeasure(1000)
    elif pipeline == 4 or pipeline == 5:
        encodings = [0]
        for en in encodings:
            # simulator = MacroSimulator(en)
            # space = {
            #     'lrd': hp.choice('lrd', [7e-4, 7.5e-4, 8e-4, 8.5e-4, 9e-4, 9.5e-4, 1e-3, 1.3e-3, 1.5e-3, 1.6e-3]),
            #     'n_neurons_d': hp.choice('n_neurons_d', [70, 80, 90, 100, 110, 120, 130, 140, 150])
            # }
            # best = fmin(
            #     fn=simulator.objective,
            #     space=space,
            #     algo=tpe.suggest,
            #     max_evals=100
            # )
            # print(best)
            # simulator = MacroSimulator(en)
            # space = {
            #     # 'lrp': hp.choice('lrp', [7e-4, 7.5e-4, 8e-4, 8.5e-4, 9e-4, 1e-3, 1.1e-3, 1.2e-3]),
            #     'lrq': hp.choice('lrq', [6e-4, 6.5e-4, 7e-4, 7.5e-4, 8e-4, 8.5e-4, 9e-4, 1e-3]),
            #     'lrd': hp.choice('lrd', [5e-4, 5.5e-4, 6e-4, 6.5e-4, 7e-4, 7.5e-4]),
            #     # 'n_neurons_p': hp.choice('n_neurons_p', [50, 60, 70, 80, 90]),
            #     'n_neurons_q': hp.choice('n_neurons_q', [70, 80, 90, 100, 110]),
            #     'n_neurons_d': hp.choice('n_neurons_d', [30, 40, 50, 60, 70, 80])
            # }
            # best = fmin(
            #     fn=simulator.objective,
            #     space=space,
            #     algo=tpe.suggest,
            #     max_evals=200
            # )
            # print(best)
            ######################
            simulator = MacroSimulator(en)
            space = {}
            if rlMode[0] == 'l':
                space.update({'lrp': hp.choice('lrp', [7e-4, 7.5e-4, 8e-4, 8.5e-4, 9e-4, 1e-3, 1.1e-3, 1.2e-3])})
                space.update({'n_neurons_p': hp.choice('n_neurons_p', [50, 60, 70, 80, 90])})
            if rlMode[1] == 'l':
                space.update({'lrq': hp.choice('lrq', [6e-4, 6.5e-4, 7e-4, 7.5e-4, 8e-4, 8.5e-4, 9e-4, 1e-3])})
                space.update({'n_neurons_q': hp.choice('n_neurons_q', [70, 80, 90, 100, 110])})
            if rlMode[3] == 'l':
                space.update({'lrd': hp.choice('lrd', [5e-4, 5.5e-4, 6e-4, 6.5e-4, 7e-4, 7.5e-4])})
                space.update({'n_neurons_d': hp.choice('n_neurons_d', [30, 40, 50, 60, 70, 80])})
            best = fmin(
                fn=simulator.objective,
                space=space,
                algo=tpe.suggest,
                max_evals=200
            )
            print(best)


if __name__=='__main__':
    main()
