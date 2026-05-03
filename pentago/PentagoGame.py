import numpy as np

from Game import Game
from .PentagoLogic import Board

_DRAW_VALUE = 0.001

SQUARE_ROT = {
    0: [0, 1, 2, 3],  # 0°
    1: [2, 0, 3, 1],  # 90° 
    2: [3, 2, 1, 0],  # 180°
    3: [1, 3, 0, 2],  # 270°
}

SQUARE_FLIP = [1, 0, 3, 2]

ROT_FLIP = [1, 0]

class PentagoGame(Game):
    def __init__(self):
        Game.__init__(self)
        self._base_board = Board()

    def getInitBoard(self):
        return self._base_board._pieces
    
    def getBoardSize(self):
        return (6, 6)
    
    def getActionSize(self):
        # size * size for placement position
        # 4 for square rotation and 2 for rotation
        return 6 * 6 * 4 * 2
    
    def getNextState(self, board, player, action):
        new_board = board.copy()
        self._base_board.update_pieces(new_board, player, action)

        return new_board, -player
    
    def getValidMoves(self, board, player):
        legal_moves = self._base_board.get_legal_moves(board)
        valids = np.zeros(self.getActionSize(), dtype=np.int8)
        valids[legal_moves] = 1
        return valids
    
    def getGameEnded(self, board, player):
        game_state = self._base_board.game_state(board, player)
        if game_state == 0:
            if not np.any(board == 0):
                return _DRAW_VALUE
            else:
                return 0
        else:
            return game_state
    
    def getCanonicalForm(self, board, player):
        return board * player
    
    def getSymmetries(self, board, pi):
        symmetries = []

        for k in range(4):
            for flip in [False, True]:
                new_board = np.rot90(board, k)
                if flip:
                    new_board = np.fliplr(new_board)

                new_pi = np.zeros_like(pi)
                for action in range(len(pi)):
                    row, col, square, rot = self._base_board.decode_action(action)

                    pos = np.array([[row, col]])
                    for _ in range(k):
                        pos = np.array([[5 - pos[0][1], pos[0][0]]])
                    new_row, new_col = pos[0]

                    if flip:
                        new_col = 5 - new_col

                    new_square = SQUARE_ROT[k][square]
                    new_rot = rot
                    if flip:
                        new_square = SQUARE_FLIP[new_square]
                        new_rot = ROT_FLIP[new_rot]

                    new_action = self._base_board.encode_action(new_row, new_col, new_square, new_rot)
                    new_pi[new_action] = pi[action]

                symmetries.append((new_board, new_pi))

        return symmetries
    
    def stringRepresentation(self, board: Board):
        return board.tobytes()
        
    @staticmethod
    def display(board):
        print(board)