import numpy as np

class RandomPlayer():
    def __init__(self, game, player_id):
        self.game = game
        self.player_id = player_id

    def play(self, board):
        valids = self.game.getValidMoves(board, self.player_id)
        valid_actions = np.where(valids == 1)[0]
        return np.random.choice(valid_actions)

