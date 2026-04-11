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
        return self._base_board._pieces.size
    
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
        pieces = board.copy()
        pieces = Board.update_pieces(pieces, player, action)
        # if player == -1:
        #     pieces = Board.flip_board(pieces)
        return (pieces, -player)
    
    def getValidMoves(self, board, player):
        legal_moves = Board.get_legal_moves(board)
        valids = np.zeros(self.getActionSize(), dtype=np.int8)
        valids[legal_moves] = 1
        return valids
    
    def getGameEnded(self, board, player):
        return Board.game_state(board, player)
    
    def getCanonicalForm(self, board, player):
        return board.copy() if player == 1 else Board.flip_board(board)
        
    def getSymmetries(self, board, pi):
        return [(board, pi)] # no symetry
    
    def stringRepresentation(self, board: Board):
        return board.tobytes()
        
    @staticmethod
    def display(board):
        print(board)