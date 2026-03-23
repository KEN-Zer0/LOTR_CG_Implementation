from os import pipe
import numpy as np
from abc import ABC, abstractmethod, abstractproperty
import Game_Model.globals
from envs.lowLevelEnv import LowLevelEnv
from envs.macroEnv import MacroEnv
from mainConfig import pipeline, rlMode, num_episodes, difficulty

class BaseSimulator(ABC):
    def __init__(self, encoding):
        self.encoding = encoding
        self.env = None
        self.setEnv()
        self.best_global_avg = -0.57

    @property
    @abstractmethod
    def agent_planning(self):
        pass

    @abstractproperty
    def agent_questing(self):
        pass

    @abstractproperty
    def agent_defense(self):
        pass

    @abstractmethod
    def setAgents(self, params):
        pass

    def setEnv(self):
        if pipeline == 1 or pipeline == 2:
            self.env = LowLevelEnv(self.encoding)
        elif pipeline == 4 or pipeline == 5:
            self.env = MacroEnv(self.encoding)

    @abstractmethod
    def rlPlanning(self, observation): # returns planning_action, next_pobservation
        pass

    @abstractmethod
    def rlQuesting(self): # returns observation, action, next_observation, reward, episode_done
        pass

    @abstractmethod
    def rlDefense(self): # returns observation, action, next_observation, reward, episode_done
        pass

    def simulatePlanning(self, observation):
        if rlMode[0] == 'l':
            return self.rlPlanning(observation)
        self.env.game.randomPlanning()
        return None, None

    def simulateQuesting(self):
        if rlMode[1] == 'l':
            return self.rlQuesting()
        self.env.game.randomQuesting()
        return None, None, None, 0, False

    def simulateDefense(self):
        if not self.env.game.getBoard().getEnemiesEngaged():
            return None, None, None, 0, False
        if not self.env.game.getPlayer().getUntappedCharacters():
            self.env.game.resolveDefense(None)
            return None, None, None, 0, False
        if rlMode[3] == 'l':
            return self.rlDefense()
        self.env.game.randomDefense()
        return None, None, None, 0, False

    @abstractmethod
    def learnPlanning(self, observation, action, reward, next_observation, episode_done):
        pass

    @abstractmethod
    def learnQuesting(self, observation, action, reward, next_observation, episode_done):
        pass

    @abstractmethod
    def learnDefense(self, observation, action, reward, next_observation, episode_done):
        pass

    def objective(self, params):
        self.setAgents(params)

        best_local_avg = -1
        score_history = []

        for i in range(num_episodes):
            Game_Model.globals.gameWin = False
            Game_Model.globals.gameOver = False
            episode_done = False
            score = 0
            if rlMode[0] == 'l': self.agent_planning().reset()
            if rlMode[1] == 'l': self.agent_questing().reset()
            if rlMode[3] == 'l': self.agent_defense().reset()
            pobservation = self.env.reset()
            while not episode_done:
                reward = 0
                planning_action, next_pobservation = self.simulatePlanning(pobservation)
                    
                qobservation, questing_action, next_qobservation, reward, episode_done = self.simulateQuesting()

                self.env.travelPhase(rlMode)

                dobservation, defense_action, next_dobservation, reward, episode_done = self.simulateDefense()

                self.env.endRound(rlMode)

                if Game_Model.globals.gameWin:
                    reward = 1
                    episode_done = True
                if Game_Model.globals.gameOver and not Game_Model.globals.gameWin:
                    reward = -1
                    episode_done = True
                
                if rlMode[0] == 'l': self.learnPlanning(pobservation, planning_action, reward, next_pobservation, episode_done)
                if rlMode[1] == 'l': self.learnQuesting(qobservation, questing_action, reward, next_qobservation, episode_done)
                if rlMode[3] == 'l': self.learnDefense(dobservation, defense_action, reward, next_dobservation, episode_done)

                pobservation = self.env.encoder.encodePlanning('critic')
                score += reward

            score_history.append(score)

            avg_score = np.mean(score_history[-1000:])
            if i % 100 == 0 and i > 1000:
                if avg_score > best_local_avg:
                    best_local_avg = avg_score
                if best_local_avg > self.best_global_avg and pipeline != 1:
                    ################## for direct action optimization #########################
                    # lrp = params['lrp']
                    # lrq = params['lrq']
                    # nnp = params['n_neurons_p']
                    # nnq = params['n_neurons_q']
                    # dirname = rlMode + 'p' + str(pipeline) + 'en' + str(self.encoding) + 'nnp' + str(nnp) + 'nnq' + str(nnq) + difficulty + 'feb'
                    # # if rlMode[0] == 'l': self.agent_planning().save_models(dirname, 'planning')
                    # # if rlMode[1] == 'l': self.agent_questing().save_models(dirname, 'questing')
                    # print(f'model with lrp {lrp}, lrq: {lrq}, nnp: {nnp}, nnq: {nnq} saved with best global avg: {self.best_global_avg}')
                    # txtname = dirname + '_sc3.txt'
                    # np.savetxt(txtname, score_history, fmt='%f', newline=' ')
                    # self.best_global_avg = best_local_avg
                    ################## for rlrrr direct action ##########################
                    # lrq = params['lrq']
                    # nnq = params['n_neurons_q']
                    # dirname = rlMode + 'p' + str(pipeline) + 'en' + str(self.encoding) + 'nnq' + str(nnq) + difficulty + 'feb'
                    # if rlMode[0] == 'l': self.agent_planning().save_models(dirname, 'planning')
                    # if rlMode[1] == 'l': self.agent_questing().save_models(dirname, 'questing')
                    # print(f'model with lrq: {lrq}, nnq: {nnq} saved with best global avg: {self.best_global_avg}')
                    # txtname = dirname + '_sc8.txt'
                    # np.savetxt(txtname, score_history, fmt='%f', newline=' ')
                    # self.best_global_avg = best_local_avg
                    ################# for macro optimization ##############################
                    dirname = rlMode + 'p' + str(pipeline) + 'en' + str(self.encoding)
                    if rlMode[0] == 'l':
                        lrp = params['lrp']
                        nnp = params['n_neurons_p']
                        dirname += 'nnp' + str(nnp)
                        print(f'lrp {lrp}, nnp {nnp}, ')
                    if rlMode[1] == 'l':
                        lrq = params['lrq']
                        nnq = params['n_neurons_q']
                        dirname += 'nnq' + str(nnq)
                        print(f'lrq {lrq}, nnq {nnq}, ')
                    if rlMode[3] == 'l':
                        lrd = params['lrd']
                        nnd = params['n_neurons_d']
                        dirname += 'nnd' + str(nnd)
                        print(f'lrd {lrd}, nnd {nnd}, ')
                    print(f'saved with best global avg: {self.best_global_avg}')
                    if pipeline == 4: dirname += 'macroAC'
                    if pipeline == 5: dirname += 'macroQ'
                    if rlMode[0] == 'l': self.agent_planning().save_models(dirname, 'planning')
                    if rlMode[1] == 'l': self.agent_questing().save_models(dirname, 'questing')
                    if rlMode[3] == 'l': self.agent_defense().save_models(dirname, 'defense')
                    self.best_global_avg = best_local_avg

            # if i % 100 == 0:
            #    print(f'episode: {i}, avg score: {avg_score}')
            
        self.env.hardReset()

        print(f'best local avg: {best_local_avg}')
        if pipeline == 1:
            return best_local_avg, score_history
        return -best_local_avg

    def loadAndTest(self, params):
        self.setAgents(params)
        # for triple optimization
        # dirname = rlMode + 'p' + str(pipeline) + 'en' + str(self.encoding) + 'nnp' + str(params['n_neurons_p']) + 'nnq' + str(params['n_neurons_q']) + 'nnd' + str(params['n_neurons_d']) + difficulty + 'macroAC'
        # for double optimization
        dirname = rlMode + 'p' + str(pipeline) + 'en' + str(self.encoding) + 'nnq' + str(params['n_neurons_q']) + 'nnd' + str(params['n_neurons_d']) + difficulty + 'macroAC'
        # for single optimization
        # dirname = rlMode + 'p' + str(pipeline) + 'en' + str(self.encoding) + 'nnd' + str(params['n_neurons_d']) + difficulty +'macroAC'
        if rlMode[0] == 'l': self.agent_planning().load_models(dirname, 'planning')
        if rlMode[1] == 'l': self.agent_questing().load_models(dirname, 'questing')
        if rlMode[3] == 'l': self.agent_defense().load_models(dirname, 'defense')

        score_history = []

        success_episodes = []
        fail_episodes = []

        for i in range(num_episodes):
            Game_Model.globals.gameWin = False
            Game_Model.globals.gameOver = False
            episode_done = False
            score = 0
            if rlMode[0] == 'l': self.agent_planning().reset()
            if rlMode[1] == 'l': self.agent_questing().reset()
            if rlMode[3] == 'l': self.agent_defense().reset()
            pobservation = self.env.reset()
            while not episode_done:
                reward = 0
                self.simulatePlanning(pobservation)
                    
                self.simulateQuesting()

                self.env.travelPhase(rlMode)

                self.simulateDefense()

                self.env.endRound(rlMode)

                if Game_Model.globals.gameWin:
                    reward = 1
                    episode_done = True
                    success_episodes.append(self.env.game.getTurnNumber())
                if Game_Model.globals.gameOver and not Game_Model.globals.gameWin:
                    reward = 0
                    episode_done = True
                    fail_episodes.append(self.env.game.getTurnNumber())
                
                pobservation = self.env.encoder.encodePlanning('critic')
                score += reward

            score_history.append(score)

        return score_history, success_episodes, fail_episodes

