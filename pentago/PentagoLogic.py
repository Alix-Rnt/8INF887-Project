import numpy as np

_EMPTY = 0

_WHITE = 1
_BLACK = -1

class Board:
    def __init__(self):
        self._pieces = np.zeros((6, 6))

    def decode_action(self, action):
        pos = action // 8
        sq_rot = action % 8
        row, col = pos // 6, pos % 6
        square = sq_rot // 2
        rot = sq_rot % 2
        return row, col, square, rot

    def encode_action(self, row, col, square, rot):
        return (row * 6 + col) * 8 + square * 2 + rot
    
    def update_pieces(self, pieces: np.ndarray, player, action):
        row, col, square, rot = self.decode_action(action)

        # place pawn
        pieces[row, col] = player

        # square rotation
        row_start = (square // 2) * 3
        col_start = (square % 2) * 3

        sub = pieces[row_start:row_start+3, col_start:col_start+3]
        pieces[row_start:row_start+3, col_start:col_start+3] = np.rot90(sub, 1 if rot == 0 else 3)

    def get_legal_moves(self, pieces):
        moves = []

        free_spaces = np.argwhere(pieces == _EMPTY)

        for row, col in free_spaces: # empty places
            for square in range(4): # squares
                for rot in range(2): # rotation
                    moves.append(self.encode_action(row, col, square, rot))
        
        return moves
    
    def has_five_aligned(self, board: np.ndarray):
        # Horizontaly
        for row in board:
            for i in range(len(row) - 4):
                if row[i] != 0 and np.all(row[i:i+5] == row[i]):
                    return row[i]

        # Verticaly
        for col in board.T:
            for i in range(len(col) - 4):
                if col[i] != 0 and np.all(col[i:i+5] == col[i]):
                    return col[i]

        # Diagonaly D-R / U-L
        for d in range(-1, 2):
            diag = np.diag(board, d)
            for i in range(len(diag) - 4):
                if diag[i] != 0 and np.all(diag[i:i+5] == diag[i]):
                    return diag[i]

        # Diagonaly D-L / U-R
        for d in range(-1, 2):
            diag = np.diag(np.fliplr(board), d)
            for i in range(len(diag) - 4):
                if diag[i] != 0 and np.all(diag[i:i+5] == diag[i]):
                    return diag[i]

        return 0
    
    def game_state(self, pieces: np.ndarray, player):
        result = self.has_five_aligned(pieces)
        if result == 0:
            return 0
        if result == player:
            return 1
        else:
            return -1
        
    def __str__(self):
        symbols = {
            _EMPTY: '.',
            _WHITE: 'W',
            _BLACK: 'B'
        }

        grid = '  ' + ' '.join(str(i) for i in range(6)) + '\n'
        for i in range(6):
            grid += str(i) + ' '
            for j in range(6):
                grid += symbols[self._pieces[i, j]] + ' '
            grid += '\n'
        return grid