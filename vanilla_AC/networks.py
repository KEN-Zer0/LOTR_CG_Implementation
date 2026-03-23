import os
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.layers import Dense

class CriticNetwork(keras.Model):
    def __init__(self, name, fc1_dims=100, fc2_dims=100):
        super(CriticNetwork, self).__init__()
        self.fc1 = Dense(fc1_dims, activation='relu')
        # self.fc2 = Dense(fc2_dims, activation='relu')
        self.v = Dense(1, activation=None)

    def call(self, state):
        value = self.fc1(state)
        # value = self.fc2(value)
        v = self.v(value)
        return v

class ActorNetwork(keras.Model):
    def __init__(self, name, n_actions, fc1_dims=100, fc2_dims=100):
        super(ActorNetwork, self).__init__()
        self.fc1 = Dense(fc1_dims, activation='relu')
        # self.fc2 = Dense(fc2_dims, activation='relu')
        self.policy = Dense(n_actions, activation='softmax')

    def call(self, state):
        value = self.fc1(state)
        # value = self.fc2(value)
        probs = self.policy(value)
        return probs