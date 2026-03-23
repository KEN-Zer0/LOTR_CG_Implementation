import os
from simulators.lowLevelSimulator import LowLevelSimulator
from simulators.macroSimulator import MacroSimulator
import Game_Model.globals
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
from main import countWins
import time
from mainConfig import pipeline, rlMode, difficulty, encoding, num_episodes

def doubleOptimization():
    dirNames = os.listdir('results')
    dirNames = [k for k in dirNames if 'en' + str(encoding) in k and 'nnp' in k and 'feb' in k]
    for dirName in dirNames:
        Game_Model.globals.init()
        n_neurons_p = dirName[13:16]
        n_neurons_p = n_neurons_p if not n_neurons_p[-1].isalpha() else n_neurons_p[0:2]
        n_neurons_q = dirName[18:22]
        n_neurons_q = n_neurons_q if not n_neurons_q[0].isalpha() else n_neurons_q[1:]
        n_neurons_q = n_neurons_q if not n_neurons_q[-1].isalpha() else n_neurons_q[:-1]
        n_neurons_q = n_neurons_q if not n_neurons_q[-1].isalpha() else n_neurons_q[:-1]
        params = { 'lrp': 0.0001, 'lrq': 0.0001, 'n_neurons_p': int(n_neurons_p), 'n_neurons_q': int(n_neurons_q) }
        if pipeline == 1 or pipeline == 2: env = LowLevelSimulator(encoding)
        if pipeline == 4 or pipeline == 5: env = MacroSimulator(encoding)
        start = time.time()
        score_history, success_episodes, fail_episodes = env.loadAndTest(params)
        end = time.time()
        countWins(dirName, score_history)
        print(f'execution time of one episode: {(end - start) / num_episodes} sec')


def main():
    doubleOptimization()

    # dirNames = os.listdir('results')
    # dirNames = [k for k in dirNames if rlMode in k and 'p' + str(pipeline) in k and 'en' + str(encoding) in k and difficulty in k]
    # for dirName in dirNames:
    #     Game_Model.globals.init()
    #     n_neurons = dirName[12:15]
    #     n_neurons = n_neurons if not n_neurons[-1].isalpha() else n_neurons[0:2]
    #     params = { 'lrq': 0.0001, 'n_neurons_q': int(n_neurons) }
    #     if pipeline == 1 or pipeline == 2: env = LowLevelSimulator(encoding)
    #     if pipeline == 4 or pipeline == 5: env = MacroSimulator(encoding)
    #     score_history = env.loadAndTest(params)
    #     countWins(dirName, score_history)

if __name__=='__main__':
    main()
