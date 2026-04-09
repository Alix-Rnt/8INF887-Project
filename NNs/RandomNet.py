from Game import Game
from NeuralNet import NeuralNet
import numpy as np

class RandomNet(NeuralNet):
    def __init__(self, game: Game):
        self.action_size = game.getActionSize()

    def predict(self, board):
        pi = np.ones(self.action_size) / self.action_size
        v = 0.0
        return pi, v

    def train(self, examples): pass
    def save_checkpoint(self, folder, filename): pass
    def load_checkpoint(self, folder, filename): pass