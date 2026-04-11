import numpy as np

"""
Chess Board.

Board is of size 8 by 8.
Board data : 
    0 = empty
    1 = pawn
    2 = knight
    3 = bishop
    4 = rook
    5 = queen
    6 = king
    positive = white
    negative = black
"""

_DRAW_VALUE = 0.001
_MAX_TURN = 200

_EMPTY = 0

_WHITE = 1
_BLACK = -1

_PAWN   = 1
_ROOK   = 2
_KNIGHT = 3
_BISHOP = 4
_QUEEN  = 5
_KING   = 6

DIRECTIONS_DELTAS = [(-1,-1),(-1, 0),(-1,+1),
                     ( 0,-1),        ( 0,+1),
                     (+1,-1),(+1, 0),(+1,+1)]

KNIGHT_MOVES = [(-2,-1),(-2,+1),(-1,-2),(-1,+2),
                (+1,-2),(+1,+2),(+2,-1),(+2,+1)]

PROMO_DIR = [-1, 0, 1]

PROMO_PIECES = [_ROOK, _KNIGHT, _BISHOP, _QUEEN]

class Board:
    def __init__(self):
        # Board is 8 by 8 + 1 line for en passant, castling and turn count
        # self._pieces[8, :4] is castling
        # self._pieces[8, 4] is en passant column
        # self._pieces[8, 5] is turn count
        self._pieces = np.zeros((9, 8), dtype=np.int16)

        self._pieces[8, :4] = 1 # castling
        self._pieces[8, 4] = -1 # en passant

        # Set pieces
        # WHITE
        self._pieces[0,0] = _ROOK   * _WHITE
        self._pieces[0,1] = _KNIGHT * _WHITE
        self._pieces[0,2] = _BISHOP * _WHITE
        self._pieces[0,3] = _QUEEN  * _WHITE
        self._pieces[0,4] = _KING   * _WHITE
        self._pieces[0,5] = _BISHOP * _WHITE
        self._pieces[0,6] = _KNIGHT * _WHITE
        self._pieces[0,7] = _ROOK   * _WHITE
        
        self._pieces[1,0] = _PAWN * _WHITE
        self._pieces[1,1] = _PAWN * _WHITE
        self._pieces[1,2] = _PAWN * _WHITE
        self._pieces[1,3] = _PAWN * _WHITE
        self._pieces[1,4] = _PAWN * _WHITE
        self._pieces[1,5] = _PAWN * _WHITE
        self._pieces[1,6] = _PAWN * _WHITE
        self._pieces[1,7] = _PAWN * _WHITE

        # BLACK
        self._pieces[7,0] = _ROOK   * _BLACK
        self._pieces[7,1] = _KNIGHT * _BLACK
        self._pieces[7,2] = _BISHOP * _BLACK
        self._pieces[7,3] = _QUEEN  * _BLACK
        self._pieces[7,4] = _KING   * _BLACK
        self._pieces[7,5] = _BISHOP * _BLACK
        self._pieces[7,6] = _KNIGHT * _BLACK
        self._pieces[7,7] = _ROOK   * _BLACK
        
        self._pieces[6,0] = _PAWN * _BLACK
        self._pieces[6,1] = _PAWN * _BLACK
        self._pieces[6,2] = _PAWN * _BLACK
        self._pieces[6,3] = _PAWN * _BLACK
        self._pieces[6,4] = _PAWN * _BLACK
        self._pieces[6,5] = _PAWN * _BLACK
        self._pieces[6,6] = _PAWN * _BLACK
        self._pieces[6,7] = _PAWN * _BLACK

    @staticmethod
    def update_pieces(pieces: np.ndarray, player, action):
        """
        action is a code from 0 to getActionSize() - 1
        action // 76 is the source
        action % 76 is the movement type
            0..55 is a simple slide
            56..63 is a knight move
            64..75 is a promotion
        """
        
        temp_action = -1
        if player == -1:
            temp_action = action
            action = Board.mirror_action(action)

        src = action // 76
        move_type = action % 76

        src_row, src_col = src // 8, src % 8

        # slide
        if move_type < 56:
            distance = move_type % 7 + 1

            dr, dc = DIRECTIONS_DELTAS[move_type // 7]
            dst_row = src_row + dr * distance
            dst_col = src_col + dc * distance

            promo = None
        # knight
        elif move_type < 64:
            dr, dc = KNIGHT_MOVES[move_type - 56]
            dst_row = src_row + dr
            dst_col = src_col + dc

            promo = None
        # promotion
        else:
            dc = PROMO_DIR[(move_type - 64) // 4]
            dst_row = src_row + player
            dst_col = src_col + dc
            
            promo = PROMO_PIECES[(move_type - 64) % 4]

        assert Board.is_valid(dst_row, dst_col), f"{dst_row, dst_col} src is {src_row, src_col} : {pieces[src_row, src_col]} from code {action} (was {temp_action})"
        # en passant
        if abs(pieces[src_row, src_col]) == _PAWN and src_col != dst_col and pieces[dst_row, dst_col] == _EMPTY:
            pieces[src_row, dst_col] = _EMPTY

        # castling
        if abs(pieces[src_row, src_col]) == _KING and abs(src_col - dst_col) == 2:
            rook_src_col = 7 if dst_col > src_col else 0
            rook_dst_col = 5 if dst_col > src_col else 3
            pieces[src_row, rook_dst_col] = pieces[src_row, rook_src_col]
            pieces[src_row, rook_src_col] = _EMPTY

        piece = pieces[src_row, src_col] # save

        # move
        pieces[dst_row, dst_col] = (promo * player if promo else pieces[src_row, src_col])
        pieces[src_row, src_col] = _EMPTY

        # update en passant availability
        pieces[8, 4] = -1
        if abs(piece) == _PAWN and abs(src_row - dst_row) == 2:
            pieces[8, 4] = dst_col

        # update castling rights
        if abs(piece) == _KING:
            pieces[8, 0 if player == 1 else 2] = 0
            pieces[8, 1 if player == 1 else 3] = 0
        dst = dst_row * 8 + dst_col
        if src == 0  or dst == 0 : pieces[8, 0] = 0
        if src == 7  or dst == 7 : pieces[8, 1] = 0
        if src == 56 or dst == 56 : pieces[8, 2] = 0
        if src == 63 or dst == 63 : pieces[8, 3] = 0

        # update turn
        pieces[8, 5] += 1

        return pieces
    
    @staticmethod
    def is_valid(x, y):
        return 0 <= x <= 7 and 0 <= y <= 7
    
    @staticmethod
    def is_checked(pieces: np.ndarray):
        king_pos = np.argwhere(pieces[:8] == _KING)
        if (len(king_pos) == 0):
            temp_b = Board()
            temp_b._pieces = pieces
            print(temp_b) 
        king_row, king_col = king_pos[0]
        
        # pawn
        row = king_row + 1
        for dc in range(-1, 2, 2):
            col = king_col + dc

            if not Board.is_valid(row, col):
                continue
            piece = pieces[row, col]

            if piece == _PAWN * -1:
                return True
            
        # knight
        for dr, dc in KNIGHT_MOVES:
            row = king_row + dr
            col = king_col + dc

            if not Board.is_valid(row, col):
                continue
            piece = pieces[row, col]

            if (piece == _KNIGHT * -1):
                return True
            
        # king
        for dr, dc in DIRECTIONS_DELTAS:
            row = king_row + dr
            col = king_col + dc
            if (not Board.is_valid(row, col)):
                continue
            piece = pieces[row, col]
            if (piece == _KING * -1):
                return True
        
        # queen, bishop, rook
        for dr, dc in DIRECTIONS_DELTAS:
            """
            Raycast overs all 8 directions
            Checks up to 7 squares
            """
            for n in range(1, 8):
                row = king_row + n * dr
                col = king_col + n * dc

                if not Board.is_valid(row, col):
                    break
                piece = pieces[row, col]

                if (piece == _EMPTY):
                    continue

                # straight
                if (abs(dr) + abs(dc) == 1):
                    if (piece == _QUEEN * -1 or piece == _ROOK * -1):
                        return True
                    else:
                        break
                    
                # diagonal
                if (abs(dr) + abs(dc) == 2):
                    if (piece == _QUEEN * -1 or piece == _BISHOP * -1):
                        return True
                    else:
                        break

        return False
    
    @staticmethod
    def mirror_action(action):
        """
        Mirrors the action such that player -1
        plays as if it was player 1
        In other words, calculate the mirror action
        """
        src = action // 76
        move_type = action % 76
        src_row, src_col = src // 8, src % 8

        new_src_row = 7 - src_row
        new_src = new_src_row * 8 + src_col

        # simple move
        if move_type < 56:
            direction = move_type // 7
            distance = move_type % 7
            dr, dc = DIRECTIONS_DELTAS[direction]
            new_dir = DIRECTIONS_DELTAS.index((-dr, dc))
            new_move_type = new_dir * 7 + distance
        # knight
        elif move_type < 64:
            k = move_type - 56
            dr, dc = KNIGHT_MOVES[k]
            new_k = KNIGHT_MOVES.index((-dr, dc))
            new_move_type = 56 + new_k
        # promotion
        else:
            new_move_type = move_type

        return new_src * 76 + new_move_type
    
    @staticmethod
    def get_legal_moves(pieces: np.ndarray):
        moves = []

        player_pieces: np.ndarray = np.argwhere(pieces[:8] > 0)
        castle_line = pieces[8, :4]
        en_passant = pieces[8, 4]

        for piece_row, piece_col in player_pieces:
            src = piece_row * 8 + piece_col

            piece = pieces[piece_row, piece_col]
            # pawn
            if (piece == _PAWN):
                # move forward
                dst_row = piece_row + 1
                dst_col = piece_col
                if (pieces[dst_row, piece_col] == _EMPTY):
                    # promotion
                    if (dst_row == 7):
                        for i in range(len(PROMO_PIECES)):
                            move_type = 64 + 1 * len(PROMO_PIECES) + i
                            moves.append(src * 76 + move_type)
                    else:
                        direction = DIRECTIONS_DELTAS.index((1, 0))
                        move_type = direction * 7
                        moves.append(src * 76 + move_type)
                    # move 2 squares
                    dst_row += 1
                    if ((piece_row == 1) and
                        Board.is_valid(dst_row, dst_col) and
                        pieces[dst_row, piece_col] == _EMPTY):
                        direction = DIRECTIONS_DELTAS.index((1, 0))
                        move_type = direction * 7 + 1
                        moves.append(src * 76 + move_type)

                # capture diagonally
                dst_row = piece_row + 1
                dst_col = piece_col - 1
                if (Board.is_valid(dst_row, dst_col) and
                    pieces[dst_row, dst_col] < 0): # opponent piece
                    if (dst_row == 7): # promotion
                        for i in range(len(PROMO_PIECES)):
                            move_type = 64 + i
                            moves.append(src * 76 + move_type)
                    else:
                        direction = DIRECTIONS_DELTAS.index((1, -1))
                        move_type = direction * 7
                        moves.append(src * 76 + move_type)
                dst_col = piece_col + 1
                if (Board.is_valid(dst_row, dst_col) and 
                    pieces[dst_row, dst_col] < 0): # opponent piece
                    if (dst_row == 7): # promotion
                        for i in range(len(PROMO_PIECES)):
                            move_type = 64 + 2 * len(PROMO_PIECES) + i
                            moves.append(src * 76 + move_type)
                    else:
                        direction = DIRECTIONS_DELTAS.index((1, 1))
                        move_type = direction * 7
                        moves.append(src * 76 + move_type)

                # en passant
                dst_row = piece_row + 1
                if (piece_row == 5):
                    dst_col = piece_col - 1
                    if (Board.is_valid(dst_row, dst_col) and
                        pieces[dst_row, dst_col] == _EMPTY and
                        en_passant != -1):
                        direction = DIRECTIONS_DELTAS.index((1, -1))
                        move_type = direction * 7
                        moves.append(src * 76 + move_type)
                    dst_col = piece_col + 1
                    if (Board.is_valid(dst_row, dst_col) and
                        pieces[dst_row, dst_col] == _EMPTY and
                        en_passant != -1):
                        direction = DIRECTIONS_DELTAS.index((1, 1))
                        move_type = direction * 7
                        moves.append(src * 76 + move_type)

            # knight
            elif (abs(piece) == _KNIGHT):
                for dr, dc in KNIGHT_MOVES:
                    dst_row = piece_row + dr
                    dst_col = piece_col + dc

                    if (Board.is_valid(dst_row, dst_col) and
                        pieces[dst_row, dst_col] <= 0): # not player piece
                        move_type = 56 + KNIGHT_MOVES.index((dr, dc))
                        moves.append(src * 76 + move_type)
            
            # king
            elif (abs(piece) == _KING):
                # regular move
                for dir_idx, (dr, dc) in enumerate(DIRECTIONS_DELTAS):
                    dst_row = piece_row + dr
                    dst_col = piece_col + dc

                    if (Board.is_valid(dst_row, dst_col) and
                        pieces[dst_row, dst_col] <= 0): # not player piece
                        direction = dir_idx
                        move_type = direction * 7
                        moves.append(src * 76 + move_type)

                # castling
                # big
                if castle_line[0] == 1:
                    if (pieces[piece_row, 1] == _EMPTY and
                        pieces[piece_row, 2] == _EMPTY and
                        pieces[piece_row, 3] == _EMPTY):
                        through = np.copy(pieces)
                        through[piece_row, 3] = through[piece_row, 4]
                        through[piece_row, 4] = _EMPTY
                        if (not Board.is_checked(pieces) and
                            not Board.is_checked(through)):
                            direction = DIRECTIONS_DELTAS.index((0, -1))
                            move_type = direction * 7 + 1
                            moves.append(src * 76 + move_type)

                # small
                if castle_line[1] == 1:
                    if (pieces[piece_row, 5] == _EMPTY and
                        pieces[piece_row, 6] == _EMPTY):
                        through = np.copy(pieces)
                        through[piece_row, 5] = through[piece_row, 4]
                        through[piece_row, 4] = _EMPTY
                        if (not Board.is_checked(pieces) and
                            not Board.is_checked(through)):
                            direction = DIRECTIONS_DELTAS.index((0, 1))
                            move_type = direction * 7 + 1
                            moves.append(src * 76 + move_type)

            # queen, bishop, rook
            else:
                for dr, dc in DIRECTIONS_DELTAS:
                    if (abs(dr) + abs(dc) == 1 and abs(piece) == _BISHOP or
                        abs(dr) + abs(dc) == 2 and abs(piece) == _ROOK):
                        continue

                    """
                    Raycast overs all 8 directions
                    Checks up to 7 squares
                    """
                    for n in range(1, 8):
                        dst_row = piece_row + n * dr
                        dst_col = piece_col + n * dc

                        if not Board.is_valid(dst_row, dst_col):
                            break
                        if pieces[dst_row, dst_col] > 0: # player piece
                            break
                        direction = DIRECTIONS_DELTAS.index((dr, dc))
                        move_type = direction * 7 + (n - 1)
                        moves.append(src * 76 + move_type)
                        if pieces[dst_row, dst_col] < 0: # opponent piece
                            break
    
        # Only keep legal moves
        # aka no check
        legal_moves = []
        for action in moves:
            new_pieces = Board.update_pieces(np.copy(pieces), 1, action)
            if not Board.is_checked(new_pieces):
                legal_moves.append(action)
        return legal_moves
    
    def flip_board(pieces: np.ndarray):
        flipped = pieces.copy()
        flipped[:8] = -np.flipud(pieces[:8])
        flipped[8, 0] = pieces[8, 2]
        flipped[8, 1] = pieces[8, 3]
        flipped[8, 2] = pieces[8, 0]
        flipped[8, 3] = pieces[8, 1]
        return flipped
    
    @staticmethod
    def game_state(pieces: np.ndarray, player):
        turn = pieces[8, 5]
        if (turn > _MAX_TURN):
            return _DRAW_VALUE
        
        unique_pieces = set(np.unique(pieces))
        unique_pieces.discard(_EMPTY)
        stalemate_combinaions = [
            {_WHITE * _KING, _BLACK * _KING},
            {_WHITE * _KING, _WHITE * _BISHOP, _BLACK * _KING},
            {_WHITE * _KING, _WHITE * _KNIGHT, _BLACK * _KING},
            {_WHITE * _KING, _BLACK * _KING, _BLACK * _BISHOP},
            {_WHITE * _KING, _BLACK * _KING, _BLACK * _KNIGHT}
        ]
        for comb in stalemate_combinaions:
            if unique_pieces == comb:
                return _DRAW_VALUE
        
        player_moves = Board.get_legal_moves(pieces)

        opp_pieces = Board.flip_board(pieces)
        opponent_moves = Board.get_legal_moves(opp_pieces)

        if (len(player_moves) == 0):
            if (Board.is_checked(pieces)):
                return -1
            else:
                return _DRAW_VALUE
        elif (len(opponent_moves) == 0):
            if (Board.is_checked(Board.flip_board(pieces))):
                return 1
            else:
                return _DRAW_VALUE
        else:
            return 0 # not finished
        
    def __str__(self):
        board = ""
        board += "  a b c d e f g h  \n"
        mapping = {
            _WHITE * _KING   : 'K',
            _WHITE * _QUEEN  : 'Q',
            _WHITE * _BISHOP : 'B',
            _WHITE * _KNIGHT : 'N',
            _WHITE * _ROOK   : 'R',
            _WHITE * _PAWN   : 'P',
            _BLACK * _KING   : 'k',
            _BLACK * _QUEEN  : 'q',
            _BLACK * _BISHOP : 'b',
            _BLACK * _KNIGHT : 'n',
            _BLACK * _ROOK   : 'r',
            _BLACK * _PAWN   : 'p',
            _EMPTY : '.'
        }
        for i in range(7, -1, -1):
            board += str(i) + " " + ' '.join([mapping.get(x, str(x)) for x in self._pieces[i]]) + " " + str(i) + "\n"
        board += "  a b c d e f g h  \n"
        return board