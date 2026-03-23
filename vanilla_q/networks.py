import os
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.layers import Dense

class Qnetwork(keras.Model):
    def __init__(self, name, n_actions, fc1_dims=100):
        super(Qnetwork, self).__init__()
        self.fc1 = Dense(fc1_dims, activation='relu')
        self.q_values = Dense(n_actions, activation=None)

    def call(self, state):
        value = self.fc1(state)
        q_values = self.q_values(value)
        return q_values