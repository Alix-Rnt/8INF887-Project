import numpy as np
import copy
import random

import Tile as t
import Player as p
import Action as a

"""HexBoard
Represents a hexagonal game board

Tiles are hexagones

Layout: (orignial layout is 60° tilted, here to the right)
   # # # #    |          (0,3) (0,4) (0,5) (0,6)          |                   (0,3) (0,4) (0,5) (0,6) |
  # # # # #   |       (1,2) (1,3) (1,4) (1,5) (1,6)       |             (1,2) (1,3) (1,4) (1,5) (1,6) |
 # # # # # #  |    (2,1) (2,2) (2,3) (2,4) (2,5) (2,6)    |       (2,1) (2,2) (2,3) (2,4) (2,5) (2,6) |
# # # # # # # | (3,0) (3,1) (3,2) (3,3) (3,4) (3,5) (3,6) | (3,0) (3,1) (3,2) (3,3) (3,4) (3,5) (3,6) |
 # # # # # #  |    (4,0) (4,1) (4,2) (4,3) (4,4) (4,5)    | (4,0) (4,1) (4,2) (4,3) (4,4) (4,5)       |
  # # # # #   |       (5,0) (5,1) (5,2) (5,3) (5,4)       | (5,0) (5,1) (5,2) (5,3) (5,4)             |
   # # # #    |          (6,0) (6,1) (6,2) (6,3)          | (6,0) (6,1) (6,2) (6,3)                   |
"""

class HexBoard:
    #----------------#
    # INTERNAL LOGIC #
    #----------------#
    def __init__(self):
        self._reset_board()

    def _reset_board(self):
        self._players = [p.Player("P1", t.Tile._W, t.Tile._C_W), p.Player("P2", t.Tile._B, t.Tile._C_B)]

        self._cities = [(0,4),(1,2),(1,5),(2,3),(2,6),(4,0),(4,3),(5,1),(5,4),(6,2)] # cities placement
        white_cities = [1, 5] # white starting cities index among cities
        black_cities = [4, 8] # black starting cities index among cities
        self._radius = 3 # 0 through 7

        self._next_player = self._players[0]
        self.board = {
            (q,r): t.Tile((q,r) in self._cities) # is city if (q,r) is in cities
            for q in range(0, 2 * self._radius + 1)
            for r in range(0, 2 * self._radius + 1)
            if abs(q + r - 2 * self._radius) <= self._radius
        }
        self._round = 0
        self._stack: list[tuple[HexBoard, p.Player, list[p.Player]]] = []

        # set starting cities
        for i in white_cities:
            self.board[self._cities[i]].city = t.Tile._C_W
        for i in black_cities:
            self.board[self._cities[i]].city = t.Tile._C_B
    
    def _is_valid(self, q, r):
        return (q,r) in self.board
    
    def _get_other_player(self, player: p.Player):
        return self._players[0] if player == self._players[1] else self._players[1]

    def _switch_player(self):
        self._next_player = self._get_other_player(self._next_player)
    
    def _neighbors(self, q, r):
        directions = [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
        return [
            (q + dq, r + dr)
            for dq, dr in directions
            if self._is_valid(q + dq, r + dr)
        ]
    
    # Return player units coordinates
    def _get_player_units(self, player: p.Player):
        units = []
        for (q,r), tile in self.board.items():
            if tile.unit == player.unit:
                units.append((q,r))
        return units
    
    # Return player cities coordinates
    def _get_player_cities(self, player: p.Player):
        cities = []
        for (q,r), tile in self.board.items():
            if tile.city == player.city:
                cities.append((q,r))
        return cities
    
    #----------------#
    # EXTERNAL LOGIC #
    #----------------#

    def copy(self):
        new_board = HexBoard.__new__(HexBoard) 
        
        new_board._radius = self._radius
        new_board._cities = self._cities
        new_board._round = self._round
        
        new_board._players = [p.copy() for p in self._players]
        new_board.board = {pos: tile.copy() for pos, tile in self.board.items()}
        
        idx = 0 if self._next_player == self._players[0] else 1
        new_board._next_player = new_board._players[idx]
        
        new_board._stack = [] 
        return new_board
    
    # Player can
    # - Force pass if no unit remain
    # - Pass
    # - Recruit unit
    # - Place a unit on an owned city
    # - Move unit by one adjacent case
    # - Capture a city
    # - Attack a adjacent enemy unit
    # - (Stack a unit)
    def player_actions(self):
        # force pass
        if (self._next_player.units_hand <= 0): return [(a.Action.FORCE_PASS,)]
        actions = []

        # pass
        actions.append((a.Action.PASS,))

        # recruit
        if (self._next_player.units_side > 0):
            actions.append((a.Action.RECRUIT,))

        # spawn
        for (q,r) in self._get_player_cities(self._next_player):
            tile = self.board[(q,r)]
            if tile.unit == t.Tile._E:
                actions.append((a.Action.SUMMON, (q,r)))
        
        for (q,r) in self._get_player_units(self._next_player):
            tile = self.board[(q,r)]
            # capture
            if tile.is_city and tile.city != self._next_player.city:
                actions.append((a.Action.CAPTURE, (q,r)))
            
            for (nq, nr) in self._neighbors(q, r):
                neighbor_tile = self.board[(nq,nr)]
                # move
                if neighbor_tile.unit == t.Tile._E:
                    actions.append((a.Action.MOVE, (q,r), (nq,nr)))
                # attack
                if neighbor_tile.unit == self._get_other_player(self._next_player).unit:
                    actions.append((a.Action.ATTACK, (q,r), (nq,nr)))

        captures = [x for x in actions if x[0] == a.Action.CAPTURE]
        attacks = [x for x in actions if x[0] == a.Action.ATTACK]
        recruit = [x for x in actions if x[0] == a.Action.RECRUIT]
        summons = [x for x in actions if x[0] == a.Action.SUMMON]
        moves = [x for x in actions if x[0] == a.Action.MOVE]
        others = [x for x in actions if x[0] not in [a.Action.CAPTURE, a.Action.ATTACK, a.Action.SUMMON, a.Action.RECRUIT, a.Action.MOVE]]

        return actions

    # Apply action on board and stack previous state on stack
    # action is a list of 1, 2 or 3 arguments
    def push(self, action):
        new_board = self.copy()
        self._stack.append((new_board.board, new_board._next_player, new_board._players))

        match action[0]:
            case a.Action.FORCE_PASS:
                pass

            case a.Action.PASS:
                self._next_player.units_hand -= 1
                self._next_player.units_used += 1

            case a.Action.RECRUIT:
                self._next_player.units_hand -= 1
                self._next_player.units_used += 2
                self._next_player.units_side -= 1

            case a.Action.SUMMON:
                self._next_player.units_hand -= 1
                from_pos = action[1]
                self.board[from_pos].unit = self._next_player.unit

            case a.Action.CAPTURE:
                self._next_player.units_hand -= 1
                self._next_player.units_used += 1
                from_pos = action[1]
                self.board[from_pos].city = self._next_player.city
                
            case a.Action.MOVE:
                self._next_player.units_hand -= 1
                self._next_player.units_used += 1
                from_pos = action[1]
                to_pos = action[2]
                self.board[to_pos].unit = self.board[from_pos].unit
                self.board[from_pos].unit = t.Tile._E

            case a.Action.ATTACK:
                self._next_player.units_hand -= 1
                self._next_player.units_used += 1
                to_pos = action[2]
                self.board[to_pos].unit = t.Tile._E
                self._get_other_player(self._next_player).units_used += 1

        # register last action
        self._next_player._last_action = action[0]
        # switch players
        self._next_player = self._get_other_player(self._next_player)
        # increment round
        self._round += 1

        if self._round % 6 == 0:
            for player in self._players:
                self.player_draw(player, 3)

    # Restore previous board state
    def pop(self):
        if not self._stack: return
        prev_board, prev_player, prev_players = self._stack.pop()
        self.board = prev_board
        self._next_player = prev_player
        self._players = prev_players
        # decrement round
        self._round -= 1
    
    # Make each player draw n units
    def player_draw(self, player: p.Player, amount):
        # if bag will be empty, put back in all used units
        if player.units_bag < amount:
            player.units_bag += player.units_used
            player.units_used = 0
        # draw units from bag
        amount_to_draw = min(amount, player.units_bag)
        player.units_bag -= amount_to_draw
        player.units_hand = amount_to_draw

    # Check if game is over
    # meaning one player has at least 6 cities
    def is_game_over(self):
        player = self._next_player
        opponent = self._get_other_player(player)
        return (len(self._get_player_cities(player)) >= 6 or # player won
                len(self._get_player_cities(opponent)) >= 6 or # opponent won
                player._last_action == a.Action.FORCE_PASS and 
                opponent._last_action == a.Action.FORCE_PASS) # both can't play
    
    # Return winner
    def get_winner(self):
        if len(self._get_player_cities(self._next_player)) >= 6:
            return self._next_player
        elif len(self._get_player_cities(self._get_other_player(self._next_player))) >= 6:
            return self._get_other_player(self._next_player)
        else:
            return None
    
    # Return winner value
    # 1 if won
    # -1 if lost
    # 0 if draw
    def get_winner_value(self):
        winner = self.get_winner()
        if winner == None: return 0 # draw
        if winner == self._next_player: return 1 # win
        else: return -1 # lose
    
    # Return tensor and vector board representation
    def parse(self):
        # board tensor
        diameter = 2 * self._radius + 1
        channels = 6
        board_tensor = np.zeros((channels, diameter, diameter), dtype=np.float32)

        player = self._next_player
        opponent = self._get_other_player(player)

        player_units = self._get_player_units(player)
        opponent_units = self._get_player_units(opponent)

        player_cities = self._get_player_cities(player)
        opponent_cities = self._get_player_cities(opponent)
        free_cities = [x for x in self._cities if x not in player_cities and x not in opponent_cities]

        for q in range(0, diameter):
            for r in range(0, diameter):
                # out of bound tiles
                if not self._is_valid(q, r):
                    for c in range(channels):
                        board_tensor[c, q, r] = -1
                # player units
                if (q,r) in player_units:
                    board_tensor[0, q, r] = 1
                # opponent units
                if (q,r) in opponent_units:
                    board_tensor[1, q, r] = 1
                # player cities
                if (q,r) in player_cities:
                    board_tensor[2, q, r] = 1
                # opponent cities
                if (q,r) in opponent_cities:
                    board_tensor[3, q, r] = 1
                # free cities
                if (q,r) in free_cities:
                    board_tensor[4, q, r] = 1
                if player == self._players[0]:
                    board_tensor[5, q, r] = 1

        board_vector = np.array([
            player.units_side / 20.0,
            player.units_bag / 20.0,
            player.units_hand / 20.0,
            player.units_used / 20.0,
            opponent.units_side / 20.0,
            opponent.units_bag / 20.0,
            opponent.units_hand / 20.0,
            opponent.units_used / 20.0,
        ], dtype=np.float32)

        return board_tensor, board_vector
    
    # Display board with print
    def __str__(self):
        grid = '\n'
        for q in range(0, 2 * self._radius + 1):
            line = ''.join(' ' for _ in range(2 * abs(self._radius - q)))
            for r in range(0, 2 * self._radius + 1):
                if not self._is_valid(q,r): 
                    continue
                tile = self.board.get((q,r))
                line += tile.unit + ' ' + tile.city + ('|' if self._is_valid(q,r+1) else '')
            grid += line + '\n'
        return grid