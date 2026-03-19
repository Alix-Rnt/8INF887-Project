class CheckersGame:
    # Board elements
    _w, _b = 'w', 'b'
    _W, _B = 'W', 'B'
    _E = '.'

    # Actions
    _CAPTURE = 0
    _MOVE = 1

    #----------------#
    # INTERNAL LOGIC #
    #----------------#
    def __init__(self, size):
        self._size = size
        self._reset_board()

    # Initialize the board data
    def _reset_board(self):
        self._next_player = self._w
        self._board = [[self._E if (i + j) % 2 == 0 else
                        self._w if i > self._size / 2 else # white pieces at front
                        self._b if i < self._size / 2 - 1 else # black pieces at back
                        self._E for j in range(self._size)] for i in range(self._size)]
        self._stack = []
    
    # Check if a position is within the board
    def _is_valid(self, i, j):
        return i >= 0 and j >= 0 and i < self._size and j < self._size

    # Return the other player
    def _get_other_player(self, player):
        return self._w if player == self._b else self._b

    # Switch the next player to the other player
    def _switch_player(self):
        self._next_player = self._get_other_player(self._next_player)

    # Return player pieces positions
    def _get_symbols(self, player):
        return (self._w, self._W) if player == self._w else (self._b, self._B)
    
    # Return player pieces positions
    def _get_pieces(self, player):
        pieces_pos = []
        for i in range(self._size):
            for j in range(self._size):
                if self._board[i][j] in self._get_symbols(player):
                    pieces_pos.append((i,j))
        return pieces_pos
    
    # Promote a piece to king if it reaches the other side
    def _promote(self, piece):
        return self._W if piece == self._w else self._B
    
    # Apply an action to the board
    def _apply_action(self, action, is_capture):
        # starting and ending positions
        si, sj = action[0]
        ei, ej = action[-1]

        piece = self._board[si][sj]

        # place piece at ending position
        # promote of it reaches other side
        if ei == 0 and piece == self._w or ei == self._size - 1 and piece == self._b:
            self._board[ei][ej] = self._promote(piece)
        else:
            self._board[ei][ej] = piece

        # remove piece at starting position
        self._board[si][sj] = self._E

        if is_capture:
            # remove every enemy piece on the path
            for a in range(len(action) - 1):
                (i,j) = action[a]
                (ni,nj) = action[a+1]
                length = abs(ni - i)
                di = int((ni - i) / length)
                dj = int((nj - j) / length)
                # raycast to find an enemy piece
                for n in range(1, length):
                    if self._board[i+di*n][j+dj*n] in self._get_symbols(self._get_other_player(self._next_player)):
                        self._board[i+di*n][j+dj*n] = self._E
                        break
    
    #----------------#
    # EXTERNAL LOGIC #
    #----------------#

    # Calculate all player available actions
    # Longer captures are prioritized over regular moves
    def player_actions(self):
        player_pieces = self._get_pieces(self._next_player)
        all_directions = [(-1,-1), (-1,1), (1,-1), (1,1)] # all four direcitons

        # captures
        # Recursive function to find capture paths
        def rec_capture(i, j, player, is_king: bool, path: list, piece_paths: list=None):
            if piece_paths is None:
                piece_paths = []
            found_capture = False
            # regular pieces
            if not is_king:
                for (di,dj) in all_directions:
                    # capture and destination zones must be on the board
                    if not self._is_valid(i+di,j+dj) or not self._is_valid(i+di*2,j+dj*2):
                        continue
                    # capture zone must be enemy piece
                    # destination zone must be empty
                    if (self._board[i+di][j+dj] in self._get_symbols(self._get_other_player(player))
                        and self._board[i+di*2][j+dj*2] == self._E):
                        found_capture = True

                        self.push(((i,j), (i+di*2, j+dj*2)), True)
                        self._next_player = self._get_other_player(self._next_player)

                        rec_capture(i+di*2, j+dj*2, player, is_king, path + [(i+di*2, j+dj*2)], piece_paths)

                        self.pop()
            # king pieces
            else:
                for (di,dj) in all_directions:
                    # raycast to find an enemy piece
                    for n in range(1, self._size):
                        # capture zone must be on the board
                        if not self._is_valid(i+di*n,j+dj*n):
                            break
                        # capture zone must be enemy piece
                        if not self._board[i+di*n][j+dj*n] in self._get_symbols(self._get_other_player(player)):
                            continue
                        # raycast to find an empty zone after the enemy piece
                        for k in range(n + 1, self._size):
                            # destination zone must be on the board
                            if not self._is_valid(i+di*k,j+dj*k):
                                break
                            # destination zone must be empty
                            if self._board[i+di*k][j+dj*k] == self._E:
                                found_capture = True

                                self.push(((i,j), (i+di*k, j+dj*k)), True)
                                self._next_player = self._get_other_player(self._next_player)

                                rec_capture(i+di*k, j+dj*k, player, is_king, path + [(i+di*k, j+dj*k)], piece_paths)

                                self.pop()
            if not found_capture and len(path) > 1:
                piece_paths.append(path)
            return piece_paths

        all_paths = []
        for (i,j) in player_pieces:
            piece = self._board[i][j]
            piece_paths = rec_capture(i, j, self._next_player, piece in (self._W, self._B), [(i,j)])

            if piece_paths:
                all_paths.extend(piece_paths)

        # get max paths and add starting piece position
        max_paths = None
        if len(all_paths) > 0:
            max_paths = [p for p in all_paths if len(p) == len(max(all_paths, key=len))]

        # if there is any capture return it
        if max_paths:
            return max_paths, True
        
        # moves
        all_moves = []
        for (i,j) in player_pieces:
            piece = self._board[i][j]
            if piece == self._w: directions = all_directions[:2]
            if piece == self._b: directions = all_directions[2:]

            # regular pieces
            if piece == self._w or piece == self._b:
                for (di,dj) in directions:
                    if self._is_valid(i+di,j+dj) and self._board[i+di][j+dj] == self._E:
                        all_moves.append(((i, j), ((i+di, j+dj))))
            # king pieces
            else:
                for (di,dj) in all_directions:
                    # raycast to find an empty zone
                    for k in range(1, self._size):
                        if self._is_valid(i+di*k,j+dj*k) and self._board[i+di*k][j+dj*k] == self._E:
                            all_moves.append(((i, j), ((i+di*k, j+dj*k))))

        return all_moves, False

    # Store board state and apply action
    def push(self, action, is_capture):
        prev_player = self._next_player
        prev_board = [row[:] for row in self._board]

        self._stack.append((prev_player, prev_board))

        self._apply_action(action, is_capture)

        self._switch_player()

    # Restore previous board state
    def pop(self):
        if not self._stack: return
        prev_player, prev_board = self._stack.pop()
        self._next_player = prev_player
        self._board = prev_board

    # Game is over if player can't move
    def is_game_over(self):
        return len(self.player_actions()[0]) == 0

    # Winner is the other player
    def get_winner(self):
        return self._get_other_player(self._next_player)

    def __str__(self):
        grid = '  ' + ' '.join(str(i) for i in range(self._size)) + "\n"
        for i in range(self._size):
            grid += str(i) + ' '
            for j in range(self._size):
                grid += self._board[i][j] + ' '
            grid += '\n'
        return grid