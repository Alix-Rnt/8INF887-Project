import numpy as np

class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valids = self.game.getValidMoves(board, 1)
        valid_actions = np.where(valids == 1)[0]
        return np.random.choice(valid_actions)

