import numpy as np

_DRAW_VALUE = 0.001

_EMPTY = 0

_WHITE = 1
_BLACK = -1

_PAWN = 1
_KING = 2

_ALL_DIRS = [(-1,-1), (-1,1), (1,-1), (1,1)]

class Board():
    """
    Initialize the Board with a size
    Initial pawn position is a diagonal pattern
    blacks at [0 ; size/2 - 1[
    white at [size/2 + 1 ; size[
    """
    def __init__(self, size):
        self._pieces = np.zeros((size, size))
        self._size = size
        
        # Setup initial pawn position
        for i in range(self._size):
            for j in range(self._size):
                if (i + j) % 2 == 0:
                    if i > self._size // 2:
                        self._pieces[i,j] = _WHITE * _PAWN
                    elif i < self._size // 2 - 1:
                        self._pieces[i,j] = _BLACK * _PAWN

    """
    Take coordinates on the board x * size + y
    and flip them to correspond to oposite point of view
    """
    def flip_coords(self, coords):
        return (self._size - coords // self._size - 1) * self._size + self._size - coords % self._size - 1
    
    """
    Applies an action to the board
    Board is NOT canonical
    """
    def update_pieces(self, pieces: np.ndarray, player, full_action, is_capture):
        src = full_action[0]
        dst = full_action[-1]

        si, sj = src // self._size, src % self._size
        ei, ej = dst // self._size, dst % self._size
        piece = pieces[si, sj]

        pieces[si, sj] = _EMPTY

        # promotion
        if abs(piece) == _PAWN and ei == (0 if player == _WHITE else self._size - 1):
            pieces[ei, ej] = player * _KING
        else:
            pieces[ei, ej] = piece
        
        if is_capture:
            for a in range(len(full_action) - 1):
                i, j = full_action[a] // self._size, full_action[a] % self._size
                ni, nj = full_action[a + 1] // self._size, full_action[a + 1] % self._size
                length = abs(ni - i)
                di = (ni - i) // length
                dj = (nj - j) // length
                # raycast to find enemy piece
                # from start to end for each action
                for n in range(1, length):
                    li, lj = i + di * n, j + dj * n
                    if pieces[li, lj] != _EMPTY and np.sign(pieces[li, lj]) != np.sign(player):
                        pieces[li, lj] = _EMPTY
                        break

        return pieces

    """
    Check if position (x,y) is on the board
    """
    def is_valid(self, x, y):
        return 0 <= x < self._size and 0 <= y < self._size
    
    """
    Return all legal actions on the board
    Board is canonical
    Actions are a list of position
    """
    def get_actions(self, pieces):
        player_pieces: np.ndarray = np.argwhere(pieces >= _WHITE)

        """
        Capture path iterates over all caputres
        """
        def rec_capture(_pieces, is_king, path: list, piece_paths):
            found = False
            i, j = path[-1] // self._size, path[-1] % self._size

            if not is_king:
                for di, dj in _ALL_DIRS:
                    ni, nj = i + di, j + dj
                    li, lj = i + di * 2, j + dj * 2
                    if not self.is_valid(ni, nj) or not self.is_valid(li, lj):
                        continue
                    if _pieces[ni, nj] <= _BLACK and _pieces[li, lj] == _EMPTY:
                        found = True
                        pieces = _pieces.copy()
                        pieces[i, j] = _EMPTY
                        pieces[ni, nj] = _EMPTY
                        pieces[li, lj] = _WHITE * _PAWN
                        rec_capture(pieces, is_king, path + [li * self._size + lj], piece_paths)
            else:
                for di, dj in _ALL_DIRS:
                    # raycast to find enemy piece
                    for n in range(1, self._size):
                        ni, nj = i + di *n, j + dj * n
                        # all squares before enemy piece must be valid and empty
                        if not self.is_valid(ni, nj) or _pieces[ni, nj] >= _WHITE:
                            break
                        if not _pieces[ni, nj] <= _BLACK:
                            continue
                        # raycast to find empty space
                        for k in range(n + 1, self._size):
                            li, lj = i + di * k, j + dj * k
                            if not self.is_valid(li, lj) or _pieces[li, lj] != _EMPTY:
                                break
                            if _pieces[li, lj] == _EMPTY:
                                found = True
                                pieces = _pieces.copy()
                                pieces[i, j] = _EMPTY
                                pieces[ni, nj] = _EMPTY
                                pieces[li, lj] = _WHITE * _KING
                                rec_capture(pieces, is_king, path + [li * self._size + lj], piece_paths)
                        break # stop raycasting after first enemy in this direction

            if not found and len(path) > 1:
                piece_paths.append(path)

        # captures
        all_paths = []
        for (i, j) in player_pieces:
            piece = pieces[i, j]
            is_king = piece == _KING

            piece_paths = []
            rec_capture(pieces, is_king, [i * self._size + j], piece_paths)
            all_paths.extend(piece_paths)

        if all_paths:
            max_len = max(len(p) for p in all_paths)
            # reduce to path of maximum length
            # then return immediately because capture has priority on move
            return [p for p in all_paths if len(p) == max_len], True
        
        # moves
        all_moves = []
        for (i, j) in player_pieces:
            piece = pieces[i, j]
            if not piece == _KING:
                # pawn can only go upwards
                for di, dj in _ALL_DIRS[:2]:
                    ni, nj = i + di, j + dj
                    if self.is_valid(ni, nj) and pieces[ni, nj] == _EMPTY:
                        all_moves.append([i * self._size + j, ni * self._size + nj])
            else:
                for di, dj in _ALL_DIRS:
                    # raycast to find empty space
                    for k in range(1, self._size):
                        ni, nj = i + di * k, j + dj * k
                        if self.is_valid(ni, nj) and pieces[ni, nj] == _EMPTY:
                            all_moves.append([i * self._size + j, ni * self._size + nj])
                        else:
                            break

        # return moves only
        return all_moves, False
    
    """
    Transforms actions to moves
    meaning each action beacomes start * size² + end
    """
    def get_legal_moves(self, pieces):
        actions, _ = self.get_actions(pieces)
        moves = []
        for action in actions:
            src = action[0]
            dst = action[-1]
            move = src * self._size ** 2 + dst
            moves.append(move)
        return moves
    
    """
    Transform a move back to a sequence of actions
    Search in all actions to find the one that correponds

    Note : should not cause any conflict since a capture
        is always maximal and a simple move is unique
    """
    def find_action(self, pieces, player, move):
        start = move // self._size ** 2
        end = move % self._size ** 2

        if player == -1:
            start = self.flip_coords(start)
            end = self.flip_coords(end)

        actions, is_capture = self.get_actions(pieces if player == 1 else self.flip_board(pieces))
        for full_action in actions:
            if player == -1:
                full_action = list(map(self.flip_coords, full_action))
            if full_action[0] == start and full_action[-1] == end:
                return full_action, is_capture
        return None, None
    
    """
    Rotate the board 180° and switch pieces black and white
    """
    def flip_board(self, pieces):
        return np.rot90(pieces, 2).copy() * -1
    
    """
    Return 1 if current player wins, -1 if they lose
    and 0 if the game is not finished
    Return _DRAW_VALUE if draw
    """
    def game_state(self, pieces: np.ndarray, player):
        player_moves = self.get_legal_moves(pieces if player == 1 else self.flip_board(pieces))
        # player loses
        if len(player_moves) == 0:
            return -1
        else:
            return 0
    
    def __str__(self):
        symbols = {
            _EMPTY:  '.',
            _WHITE * _PAWN: 'w',
            _WHITE * _KING: 'W',
            _BLACK * _PAWN: 'b',
            _BLACK * _KING: 'B',
        }
        grid = '  ' + ' '.join(str(i) for i in range(self._size)) + '\n'
        for i in range(self._size):
            grid += str(i) + ' '
            for j in range(self._size):
                grid += symbols[self._pieces[i, j]] + ' '
            grid += '\n'
        return grid