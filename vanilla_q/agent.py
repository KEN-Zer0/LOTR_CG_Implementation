import os
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.optimizers import Adam
from vanilla_q.networks import Qnetwork

class QAgent():
    def __init__(self, name, n_actions, lr=0.00001, n_neurons=100, gamma=0.99):
        self.q_network = Qnetwork(name, n_actions, n_neurons)
        self.q_network.compile(optimizer=Adam(learning_rate=lr))
        self.gamma = gamma

    def save_models(self, dirname, filename):
        self.q_network.save_weights(os.path.join('results/', dirname, filename + '_qnetwork'))

    def load_models(self, dirname, filename):
        self.q_network.load_weights(os.path.join('results/', dirname, filename + '_qnetwork'))

    def choose_action(self, observation):
        state = tf.convert_to_tensor([observation])
        q_values = self.q_network(state)
        q_values = tf.squeeze(q_values)
        return [np.argmax(q_values)]

    def learn(self, action, observation, reward, next_observation):
        state = tf.convert_to_tensor([observation], dtype=tf.float32)
        next_state = tf.convert_to_tensor([next_observation], dtype=tf.float32)
        with tf.GradientTape(persistent=True) as tape:
            q_current = self.q_network(state)
            q_current = tf.squeeze(q_current)
            q_next = self.q_network(next_state)
            q_next = tf.squeeze(q_next)
            maxQ1 = tf.reduce_max(q_next)
            q_target = tf.Variable(q_current) 
            q_target[action].assign(reward + self.gamma * maxQ1)
            loss = q_target - q_current

        q_network_gradient = tape.gradient(loss, self.q_network.trainable_variables)
        self.q_network.optimizer.apply_gradients(zip(q_network_gradient, self.q_network.trainable_variables))

    def reset(self):
        pass