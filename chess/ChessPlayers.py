import numpy as np

class RandomPlayer():
    def __init__(self, game, player_id):
        self.game = game
        self.player_id = player_id

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, self.player_id)
        while valids[a] != 1:
            a = np.random.randint(self.game.getActionSize())
        return a

