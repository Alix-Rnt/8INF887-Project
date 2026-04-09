import numpy as np

from Game import Game
from .ChessLogic import Board

class ChessGame(Game):
    def __init__(self):
        Game.__init__(self)
        self._base_board = Board()

    def getInitBoard(self):
        return self._base_board._pieces.copy()
    
    def getBoardSize(self):
        return (10, 8)
    
    def getActionSize(self):
        """
        64 = Each piece comes from on of the 64 squares
        *
        56 = Queen, Rooks and Bishops can move in up to 8 directions * 7 squares (simplified)
        8  = Knights can move in an L-shape up to 8 squares
        12 = Pawns can promote into 4 pieces from 3 different directions
        """
        return 64 * (56 + 8 + 12) # 64 * 76 = 4864
    
    def getNextState(self, board, player, action):
        pieces = np.copy(board)
        real_action = Board.mirror_action(action) if player == -1 else action
        pieces = Board.update_pieces(pieces, player, real_action)
        return (pieces, -player)
    
    def getValidMoves(self, board, player):
        valids = np.zeros(self.getActionSize(), dtype=np.int8)
        legal_moves = Board.get_legal_moves(board)
        if player == -1:
            legal_moves = [Board.mirror_action(a) for a in legal_moves]
        valids[legal_moves] = 1
        return valids
    
    def getGameEnded(self, board, player):
        return Board.game_state(board, player)
    
    def getCanonicalForm(self, board, player):
        if player == 1:
            return board.copy()
        canonical = board.copy()
        canonical[:8] = -np.flipud(board[:8])
        canonical[9][0] = board[9][2]
        canonical[9][1] = board[9][3]
        canonical[9][2] = board[9][0]
        canonical[9][3] = board[9][1]
        return canonical
        
    def getSymmetries(self, board, pi):
        return [(board, pi)] # no symetry
    
    def stringRepresentation(self, board: Board):
        return board.tobytes()
        
    @staticmethod
    def display(board):
        print(board)