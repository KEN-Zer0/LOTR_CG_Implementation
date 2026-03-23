import os
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.optimizers import Adam
import tensorflow_probability as tfp
from vanilla_AC.networks import CriticNetwork, ActorNetwork

class Agent():
    def __init__(self, name, n_actions=2, critic_lr=0.0001, actor_lr=0.0001, n_neurons=100, gamma=0.99):
        self.critic = CriticNetwork(name, n_neurons, n_neurons)
        self.critic.compile(optimizer=Adam(learning_rate=critic_lr))
        self.actor = ActorNetwork(name, n_actions, n_neurons, n_neurons)
        self.actor.compile(optimizer=Adam(learning_rate=actor_lr))
        self.gamma = gamma
        self.current_discount = 1.0
        self.state = None
        self.action = None

    def save_models(self, dirname, filename):
        self.critic.save_weights(os.path.join('results/', dirname, filename + '_critic'))
        self.actor.save_weights(os.path.join('results/', dirname, filename + '_actor'))

    def load_models(self, dirname, name):
        self.critic.load_weights(os.path.join('results', dirname, name + '_critic'))
        self.actor.load_weights(os.path.join('results', dirname, name + '_actor'))

    def setState(self, observation):
        self.state = tf.convert_to_tensor([observation])

    def setAction(self, action):
        self.action = tf.convert_to_tensor([action])

    def choose_action(self, observation):
        self.state = tf.convert_to_tensor([observation])
        probs = self.actor(self.state)
        action_probabilities = tfp.distributions.Categorical(probs=probs)
        self.action = action_probabilities.sample()
        return self.action.numpy()

    def choose_action_planning(self, observation):
        state = tf.convert_to_tensor([observation])
        probs = self.actor(state)
        probs = tf.squeeze(probs)
        if tf.rank(probs).numpy() == 1:
            return 0
        return tf.argmax(probs).numpy()[1]

    def learn(self, observation, reward, next_observation, done):
        state = tf.convert_to_tensor([observation], dtype=tf.float32)
        next_state = tf.convert_to_tensor([next_observation], dtype=tf.float32)
        reward = tf.convert_to_tensor(reward, dtype=tf.float32)
        with tf.GradientTape(persistent=True) as tape:
            state_value = self.critic(state)
            next_state_value = self.critic(next_state)
            state_value = tf.squeeze(state_value)
            next_state_value = tf.squeeze(next_state_value)

            delta = reward + self.current_discount * next_state_value * (1 - int(done)) - state_value
            critic_loss = delta**2

            probs = self.actor(self.state)
            action_probs = tfp.distributions.Categorical(probs=probs)
            log_prob = action_probs.log_prob(self.action)
            actor_loss = -self.current_discount * delta * log_prob

        critic_network_gradient = tape.gradient(critic_loss, self.critic.trainable_variables)
        self.critic.optimizer.apply_gradients(zip(critic_network_gradient, self.critic.trainable_variables))

        actor_network_gradient = tape.gradient(actor_loss, self.actor.trainable_variables)
        self.actor.optimizer.apply_gradients(zip(actor_network_gradient, self.actor.trainable_variables))

        self.current_discount *= self.gamma
    
    def reset(self):
        self.current_discount = 1.0


