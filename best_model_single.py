import os
from simulators.lowLevelSimulator import LowLevelSimulator
from simulators.macroSimulator import MacroSimulator
import Game_Model.globals
import numpy as np
import time
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
from main import countWins
from mainConfig import pipeline, rlMode, difficulty, encoding, num_episodes

## only for single agent!!!!

def main():
    dirName = 'rlrlrp5en0nnq70nnd70easymacroAC'
    Game_Model.globals.init()
    ############## for single ##############
    # n_neurons = dirName[13:16]
    # n_neurons = n_neurons if not n_neurons[-1].isalpha() else n_neurons[0:2]
    # params = { 'lrd': 0.0001,'n_neurons_d': n_neurons }
    ################ for double ###############
    n_neurons_q = dirName[13:16]
    n_neurons_q = n_neurons_q if not n_neurons_q[-1].isalpha() else n_neurons_q[0:2]
    n_neurons_d = dirName[18:21]
    n_neurons_d = n_neurons_d if not n_neurons_d[-1].isalpha() else n_neurons_d[0:2]
    params = { 'lrq': 0.0001, 'lrd': 0.0001, 'n_neurons_q': n_neurons_q, 'n_neurons_d': n_neurons_d }
    ############### for triple #################
    # n_neurons_p = dirName[13:16]
    # print(n_neurons_p)
    # n_neurons_p = n_neurons_p if not n_neurons_p[-1].isalpha() else n_neurons_p[0:2]
    # n_neurons_q = dirName[18:21]
    # print(n_neurons_q)
    # n_neurons_q = n_neurons_q if not n_neurons_q[-1].isalpha() else n_neurons_q[0:2]
    # n_neurons_d = dirName[23:25]
    # print(n_neurons_d)
    # n_neurons_d = n_neurons_d if not n_neurons_d[-1].isalpha() else n_neurons_d[0:2]
    # params = { 'lrp': 0.0001, 'lrq': 0.0001, 'lrd': 0.0001, 'n_neurons_p': n_neurons_p, 'n_neurons_q': n_neurons_q, 'n_neurons_d': n_neurons_d }
    if pipeline == 1 or pipeline == 2: env = LowLevelSimulator(encoding)
    if pipeline == 4 or pipeline == 5: env = MacroSimulator(encoding)
    start = time.time()
    score_history, successEpisodes, failEpisodes = env.loadAndTest(params)
    end = time.time()
    successEpisodes = [su + 1 for su in successEpisodes if su]
    failEpisodes = [fa + 1 for fa in failEpisodes if fa]
    np.savetxt('successEpisodes.txt', successEpisodes, fmt='%d', newline=' ')
    np.savetxt('failEpisodes.txt', failEpisodes, fmt='%d', newline=' ')
    countWins(dirName, score_history)
    print(f'execution time of one episode: {(end - start) / num_episodes} sec')

if __name__=='__main__':
    main()
