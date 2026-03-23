import numpy as np
from simulators.baseSimulator import BaseSimulator
from vanilla_AC.agent import Agent
from vanilla_q.agent import QAgent
from mainConfig import pipeline, rlMode

class MacroSimulator(BaseSimulator):
    def __init__(self, encoding):
        super(MacroSimulator, self).__init__(encoding)
        self.agent_p = None
        self.agent_q = None
        self.agent_d = None

    def agent_planning(self):
        return self.agent_p

    def agent_questing(self):
        return self.agent_q

    def agent_defense(self):
        return self.agent_d

    def setAgents(self, params):
        if rlMode[0] == 'l':
            if pipeline == 4: self.agent_p = Agent('planning', 7, params['lrp'], params['lrp'], params['n_neurons_p'])
            elif pipeline == 5: self.agent_p = QAgent('planning', 7, params['lrp'], params['n_neurons_p'])
        if rlMode[1] == 'l':
            if pipeline == 4: self.agent_q = Agent('questing', 7, params['lrq'], params['lrq'], params['n_neurons_q'])
            elif pipeline == 5: self.agent_q = QAgent('questing', 7, params['lrq'], params['n_neurons_q'])
        if rlMode[3] == 'l':
            if pipeline == 4: self.agent_d = Agent('defense', 4, params['lrd'], params['lrd'], params['n_neurons_d'])
            elif pipeline == 5: self.agent_d = QAgent('defense', 4, params['lrd'], params['n_neurons_d'])
        
    def rlPlanning(self, observation):
        if len(self.env.encoder.encodePlanning('macro')) != 0:
            action = self.agent_p.choose_action(observation)
            next_observation = self.env.step_planning(action) 
            return action, next_observation

    def rlQuesting(self):
        observation = self.env.encoder.encodeQuesting('macro')
        if len(observation) != 0:
            action = self.agent_q.choose_action(observation)
            next_observation, reward, episode_done = self.env.step_questing(action)
            return observation, action, next_observation, reward, episode_done
        return observation, None, self.env.encoder.encodeQuesting('macro'), 0, False

    def rlDefense(self):
        observation = self.env.encoder.encodeDefense('macro')
        if len(observation) != 0:
            action = self.agent_d.choose_action(observation)
            next_observation, reward, episode_done = self.env.step_defense(action)
            return observation, action, next_observation, reward, episode_done
        return observation, None, self.env.encoder.encodeDefense('macro'), 0, False  

    def learnPlanning(self, observation, action, reward, next_observation, episode_done):
        if len(next_observation) != 0:
            if pipeline == 4:
                self.agent_p.learn(observation, reward, next_observation, episode_done)
            elif pipeline == 5:
                self.agent_p.learn(action[0], observation, reward, next_observation)

    def learnQuesting(self, observation, action, reward, next_observation, episode_done):
        if len(next_observation) != 0:
            if pipeline == 4:
                self.agent_q.learn(observation, reward, next_observation, episode_done)
            elif pipeline == 5:
                self.agent_q.learn(action[0], observation, reward, next_observation)

    def learnDefense(self, observation, action, reward, next_observation, episode_done):
        if not action: return
        if pipeline == 4:
            self.agent_d.learn(observation, reward, next_observation, episode_done)
        elif pipeline == 5:
            self.agent_d.learn(action[0], observation, reward, next_observation)
    