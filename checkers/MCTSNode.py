import math
import random
import time
from tqdm import tqdm

import CheckersGame as g

MAX_ROUNDS = 200

class MCTSNode:
    def __init__(self, state: g.CheckersGame, parent=None, action=None, player=None):
        self.state: g.CheckersGame = state
        self.parent = parent
        self.action = action        
        self.player = player         
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_actions, self.is_capture = state.player_actions()

    def is_terminal(self):
        return self.state.is_game_over()

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def expand(self):
        action = self.untried_actions.pop()

        new_state = self.state.copy()
        player_who_played = new_state._next_player
        new_state.apply_move(action, self.is_capture)
        child = MCTSNode(new_state, parent=self, action=action, player=player_who_played)

        self.children.append(child)
        return child

    def best_child(self, c=1.4):
        for child in self.children:
            if child.visits == 0:
                return child

        def ucb(child):
            exploit = child.wins / child.visits
            explore = c * math.sqrt(math.log(self.visits) / child.visits)
            return exploit + explore

        return max(self.children, key=ucb)

    def backpropagate(self, winner):
        self.visits += 1

        if self.player is not None:
            if winner is None:
                self.wins += 0.5
            elif winner == self.player:
                self.wins += 1.0

        if self.parent:
            self.parent.backpropagate(winner)

    def rollout(self):
        new_state = self.state.copy()

        for _ in range(MAX_ROUNDS):
            winner = new_state.get_winner()
            if winner is not None:
                return winner
            actions, is_capture = new_state.player_actions()
            move = random.choice(actions)
            new_state.apply_move(move, is_capture)
        return None

def mcts_search(root_state, iterations=500):
    root = MCTSNode(root_state, player=None)

    for _ in range(iterations):
        node: MCTSNode = root

        while not node.is_terminal() and node.is_fully_expanded():
            node = node.best_child()

        if not node.is_terminal() and not node.is_fully_expanded():
            node = node.expand()

        winner = node.rollout()

        node.backpropagate(winner)

    best = max(root.children, key=lambda c: c.visits)
    return best.action

def play_game(iterations=500, verbose=False):
    board = g.CheckersGame(10)

    round = 0

    while not board.is_game_over() and round < MAX_ROUNDS:
        if verbose: print("\n" + "="*30)
        if verbose: print(board)
        if verbose: time.sleep(0.5)
        if verbose: print(f"It's player {board._next_player} to play")

        actions, is_capture = board.player_actions()

        if not actions:
            raise ValueError("No action available")
        
        if verbose: print(f"Available actions for player {board._next_player} :")
        if verbose: print(f"{'Capture' if is_capture else 'Move'} x{len(actions)}")

        if board._next_player == board._WHITE:
            action = mcts_search(board, iterations)
            if verbose: print(f"MCTS action : {action}")
        else:
            action = random.choice(actions)
            if verbose: print(f"Random action : {action}")

        board = board.apply_move(action, is_capture)

        round += 1

    if verbose: print("\n" + "="*30)
    if verbose: print(board)

    if round < MAX_ROUNDS:
        if verbose: print(f"{board.get_winner()} won !")
        return 'w' if board.get_winner() == board._WHITE else 'b'
    else:
        if verbose: print(f"Tie !")
        return 'n'
    
if __name__ == "__main__":
    # print(play_game(True))

    winners = {'w':0, 'b':0, 'n':0}
    for i in tqdm(range(100)):
        winners[play_game(500, True)] += 1
    print(winners)

    # results: list[tuple] = []

    # for iterations in tqdm(range(10, 110, 10)):
    #     winners = {'w':0, 'b':0, 'n':0}
    #     for i in tqdm(range(100)):
    #         winners[play_game(iterations)] += 1
    #     results.append((iterations, winners['w'], winners['b'], winners['n']))
    #     print(results[-1])
    # print(results)