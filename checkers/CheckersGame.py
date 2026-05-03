import numpy as np

from Game import Game
from .CheckersLogic import Board

_DRAW_VALUE = 0.001
_MAX_PROGRESS = 20

class CheckersGame(Game):
    def __init__(self, size=10):
        Game.__init__(self)
        self.size = size
        self._base_board = Board(size)

    def getInitBoard(self):
        board = np.zeros((self.size + 1, self.size))
        board[:-1] = self._base_board._pieces
        return board

    def getBoardSize(self):
        return (self.size, self.size)

    def getActionSize(self):
        # size * size for start position 
        # and size * size for end position
        # Result : size ** 4
        return self._base_board._size ** 4
    
    def getNextState(self, board, player, action):
        pieces = board[:-1]
        no_progress = board[-1, 0]

        full_action, is_capture = self._base_board.find_action(pieces, player, action)
        
        si, sj = full_action[0] // self.size, full_action[0] % self.size
        piece_moved = pieces[si, sj]

        new_board = board.copy()
        self._base_board.update_pieces(new_board[:-1], player, full_action, is_capture)
        
        if is_capture:
            new_board[-1, 0] = 0
        else:
            new_board[-1, 0] = no_progress + 1
        
        return new_board, -player
    
    def getValidMoves(self, board, player):
        legal_moves = self._base_board.get_legal_moves(board[:-1])
        valids = np.zeros(self.getActionSize(), dtype=np.int8)
        valids[legal_moves] = 1
        return valids

    def getGameEnded(self, board, player):
        pieces = board[:-1]
        no_progress = board[-1, 0]
        
        if no_progress >= _MAX_PROGRESS:
            return _DRAW_VALUE
        
        return self._base_board.game_state(pieces, player)

    def getCanonicalForm(self, board, player):
        new_board = board.copy()
        new_board[:-1] *= player
        if player == -1:
            new_board[:-1] = self._base_board.flip_board(board[:-1])
        return new_board

    def getSymmetries(self, board, pi):
        pieces = board[:-1]
        meta = board[-1:]
        
        pieces_flip = np.fliplr(pieces).copy()
        
        pi_4d = np.reshape(pi, (self.size, self.size, self.size, self.size))
        
        pi_flip = np.flip(pi_4d, axis=(1, 3)).flatten()
        
        board_flip = np.vstack([pieces_flip, meta])
        
        return [(board, pi), (board_flip, pi_flip)]
    
    def stringRepresentation(self, board: Board):
        return board.tobytes()
        
    @staticmethod
    def display(board):
        print(board)