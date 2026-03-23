from Game_Model.game import Game
from macroEnv import MacroEnv
import Game_Model.globals
from vanilla_AC.agent import Agent
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
from main import countWins
from mainConfig import difficulty

Game_Model.globals.init()

num_episodes = 10000

filename = 'llrrr-hard-en1-macro'

def main():
    if filename[0] == 'l':
        agent_planning = Agent('planning', 3)
        agent_planning.load_models(filename, 'planning')
    if filename[1] == 'l':
        agent_questing = Agent('questing', 3)
        agent_questing.load_models(filename, 'questing')
    env = MacroEnv() ############### set appriopriate env along with filename !!!!!!!!
    score_history = []

    for i in range(num_episodes):
        Game_Model.globals.gameWin = False
        Game_Model.globals.gameOver = False
        episode_done = False
        score = 0
        if filename[0] == 'l': agent_planning.reset()
        if filename[1] == 'l': agent_questing.reset()
        pobservation = env.reset()
        while not episode_done:
            ########################### Planning #####################
            if filename[0] == 'l':
                if len(env.featuresPlanning()) != 0:
                    planning_action = agent_planning.choose_action(pobservation)
                    next_pobservation = env.step_planning(planning_action) 
            else:
                env.game.randomPlanning()
                reward = 0

            if filename[1] == 'l':
                qobservation = env.featuresQuesting()
                if len(env.featuresQuesting()) != 0:
                    questing_action = agent_questing.choose_action(qobservation)
                    next_qobservation, reward, episode_done = env.step_questing(questing_action)
            else:
                env.game.randomQuesting()
                reward = 0
            
            env.endRound(filename)

            if Game_Model.globals.gameWin:
                reward = 1
                episode_done = True    
            if Game_Model.globals.gameOver and not Game_Model.globals.gameWin:
                reward = 0
                episode_done = True
            

            pobservation = env.featuresPlanning()
            score += reward

        score_history.append(score)

    countWins(filename[:5], score_history)


if __name__=='__main__':
    main()
