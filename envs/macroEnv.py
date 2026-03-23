from numpy.lib.histograms import _histogram_bin_edges_dispatcher
from envs.baseEnv import BaseEnv
from mainConfig import difficulty

class MacroEnv(BaseEnv):
    def __init__(self, encoderType):
        super(MacroEnv, self).__init__(encoderType)

    def step_planning(self, action):
        self.game.macroPlanning(action[0])
        return self.encoder.encodePlanning('macro')

    def step_questing(self, action):
        self.game.macroQuesting(action[0])
        return self.encoder.encodeQuesting('macro'), 0, False
    
    def step_defense(self, action):
        self.game.macroDefense(action[0])
        return self.encoder.encodeDefense('macro'), 0, False

    def reset(self):
        super().reset()
        return self.encoder.encodePlanning('macro')
