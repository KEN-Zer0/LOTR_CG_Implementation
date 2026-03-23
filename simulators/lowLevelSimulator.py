from simulators.baseSimulator import BaseSimulator
from vanilla_AC.agent import Agent
from mainConfig import rlMode

class LowLevelSimulator(BaseSimulator):
    def __init__(self, encoding):
        super(LowLevelSimulator, self).__init__(encoding)
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
        if rlMode[0] == 'l': self.agent_p = Agent('planning', 2, params['lrp'], params['lrp'], params['n_neurons_p'])
        if rlMode[1] == 'l': self.agent_q = Agent('questing', 2, params['lrq'], params['lrq'], params['n_neurons_q'])
        if rlMode[3] == 'l': self.agent_d = Agent('defense', 2, params['lrd'], params['lrd'], params['n_neurons_d'])

    def rlPlanning(self, observation):
        if len(self.env.encoder.encodePlanning('actor')) != 0:
            self.agent_p.setState(self.env.encoder.encodePlanning('actor'))

            while True:
                current_planning_state = self.env.encoder.encodePlanning('actor')
                if not len(current_planning_state):
                    break
                current_planning_action = self.agent_p.choose_action_planning(current_planning_state)
                self.env.step_planning(current_planning_action)
            self.agent_p.setAction(self.env.planning_action)
        return None, self.env.encoder.encodePlanning('critic')

    def rlQuesting(self):
        observation = self.env.encoder.encodeQuesting('critic')
        if len(self.env.encoder.encodeQuesting('actor')) != 0:
            questing_action = self.agent_q.choose_action(self.env.encoder.encodeQuesting('actor'))
            next_observation, reward, episode_done = self.env.step_questing(questing_action)
            return observation, questing_action, next_observation, reward, episode_done
        return observation, None, self.env.encoder.encodeQuesting('critic'), 0, False

    def rlDefense(self):
        observation = self.env.encoder.encodeDefense('critic')
        if len(self.env.encoder.encodeDefense('actor')) != 0:
            defense_action = self.agent_d.choose_action(self.env.encoder.encodeDefense('actor'))
            next_observation, reward, episode_done = self.env.step_defense(defense_action)
            return observation, defense_action, next_observation, reward, episode_done
        return observation, None, self.env.encoder.encodeDefense('critic'), 0, False

    def learnPlanning(self, observation, action, reward, next_observation, episode_done):
        if len(self.env.encoder.encodePlanning('actor')) != 0:
            self.agent_p.learn(observation, reward, next_observation, episode_done)

    def learnQuesting(self, observation, action, reward, next_observation, episode_done):
        if len(self.env.encoder.encodeQuesting('actor')) != 0:
            self.agent_q.learn(observation, reward, next_observation, episode_done)

    def learnDefense(self, observation, action, reward, next_observation, episode_done):
        print(action)
        if not action: return
        self.agent_d.learn(observation, reward, next_observation, episode_done)