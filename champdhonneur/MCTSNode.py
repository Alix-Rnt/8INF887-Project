import math
import random

import CHGame as b
import Player as p

"""
Monte Carlo Tree Search implementation
Code inspired by https://www.geeksforgeeks.org/machine-learning/monte-carlo-tree-search-mcts-in-machine-learning
Coherent with HexBoard implementation
"""
class MCTSNode:
    def __init__(self, parent=None, action=None, player=None, untried_actions=None):
        self.parent: MCTSNode = parent
        self.action = action
        self.player: p.Player = player
        self.children: list[MCTSNode] = []
        self.visits = 0
        self.wins = 0.0
        self.untried_actions: list = untried_actions

    def is_terminal(self, board: b.HexBoard):
        return board.is_game_over() # or not available_actions(self.state)
    
    def is_fully_expanded(self):
        return len(self.untried_actions) == 0
    
    def expand(self, board: b.HexBoard):
        player = board._next_player
        action = self.untried_actions.pop()
        board.push(action)

        child = MCTSNode(parent=self, action=action, player=player, untried_actions=board.player_actions())
        board.pop()
        self.children.append(child)
        return child
    
    def best_child(self, c=1.4):
        for child in self.children:
            if child.visits == 0:
                return child

        def ucb(child: MCTSNode):
            exploit = child.wins / child.visits
            explore = c * math.sqrt(math.log(self.visits) / child.visits)
            return exploit + explore

        return max(self.children, key=ucb)

    def rollout_in_place(self, board: b.HexBoard):
        history = []

        max_round = 50
        round = 0

        while not board.is_game_over() and round < max_round:
            actions = board.player_actions()
            if not actions: # cannot actually be true
                print("NO ACTION")
                return None
            action = random.choice(actions)
            board.push(action) # automatically changes player
            history.append(action)
            round += 1

        return history
    
    def score(self, player: p.Player, board: b.HexBoard):
        f_cities = 0.2 # points per owned city
        f_units = 0.01 # points per unit
        f_units_on_city = 0.05 # points per unit on a not owned city

        opponent = board._get_other_player(player)

        player_cities = board._get_player_cities(player)
        opponent_cities = board._get_player_cities(opponent)

        sp_cities = len(player_cities)
        so_cities = len(opponent_cities)

        player_units = board._get_player_units(player)

        sp_units = len(player_units)

        sp_units_on_city = sum(1 for u in player_units if u in board._cities and u not in player_cities)
        
        return max(-0.9, min(0.9,
                             (sp_cities) * f_cities +
                             (sp_units_on_city) * f_units_on_city))

    def backpropagate(self, board: b.HexBoard):
        self.visits += 1

        winner = board.get_winner()

        if self.player is not None:
            if winner is not None:
                reward = 1.0 if winner._name == self.player._name else -1.0
            else:
                reward = self.score(self.player, board)

            self.wins += reward

        if self.parent:
            self.parent.backpropagate(board)

def mcts_search(root_state: b.HexBoard, iterations=500):
    root = MCTSNode(player=None, untried_actions=root_state.player_actions())

    for i in range(iterations):
        board = root_state.copy()
        history = []
        node = root

        while not node.is_terminal(board) and node.is_fully_expanded():
            node = node.best_child()
            board.push(node.action)
            history.append(node.action)

        if not node.is_terminal(board) and not node.is_fully_expanded():
            node = node.expand(board)
            board.push(node.action)
            history.append(node.action)

        rollout_history = node.rollout_in_place(board)
        node.backpropagate(board)

        for _ in range(len(rollout_history)):
            board.pop()
        for _ in range(len(history)):
            board.pop()

    for child in root.children:
        print(f"Action: {child.action}, Visites: {child.visits}, Wins: {child.wins/child.visits:.2f}")
    # time.sleep(1)
    best = max(root.children, key=lambda c: c.visits)

    return best.action