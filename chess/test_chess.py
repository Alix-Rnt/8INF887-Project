import time
import os
import numpy as np
from argparse import Namespace

from .ChessPlayers import RandomPlayer
from .ChessGame import ChessGame
from .ChessLogic import Board
from .ChessNet import ChessNetWrapper
from .ChessVisualizer import ChessVisualizer
from Arena import Arena
from MCTS import MCTS

CHESS_DIR = os.path.dirname(os.path.abspath(__file__))

def play_game(verbose=False):
    game = ChessGame()
    p1 = RandomPlayer(game, 1)
    p2 = RandomPlayer(game, -1)

    board, player = game.getInitBoard(), 1

    if verbose: print("BEGIN")
    
    while game.getGameEnded(board, player) == 0:
        player_pieces = (board[:8] < 0).sum() if player == -1 else (board[:8] > 0).sum()

        if verbose: print(f"Player {player}")
        canonical_board = game.getCanonicalForm(board, player)
        if verbose: print("======== CANONICAL ========")
        temp_b = Board()
        temp_b._pieces = canonical_board
        if verbose: print(temp_b)

        if player == p1.player_id:
            action = p1.play(canonical_board)
        else:
            action = p2.play(canonical_board)
        board, player = game.getNextState(board, player, action)
        if verbose: print("========")
        temp_b = Board()
        temp_b._pieces = board
        if verbose: print(temp_b)

        assert(player_pieces == ((board[:8] < 0).sum() if player == 1 else (board[:8] > 0).sum()))
        # if verbose : time.sleep(1)
    
    game_end = game.getGameEnded(board, player)
    if (game_end == 0.001):
        if verbose: print("Draw")
    else:
        if verbose: print(f"Player {player} {'won' if game_end == 1 else 'lost'}")
    if (player == game_end):
        return 1
    elif (game_end == 2):
        return 0
    else:
        return -1
    
def get_game_history(arena):
    """Lance une partie et récupère tous les plateaux"""
    board = arena.game.getInitBoard()
    history = [board.copy()]
    curPlayer = 1
    
    while arena.game.getGameEnded(board, curPlayer) == 0:
        action = arena.player1(arena.game.getCanonicalForm(board, curPlayer)) if curPlayer == 1 \
                 else arena.player2(arena.game.getCanonicalForm(board, curPlayer))
        
        board, curPlayer = arena.game.getNextState(board, curPlayer, action)
        history.append(board.copy())
        
    return history    

if __name__ == "__main__":
    # play_game(True)

    # winners = {1: 0, -1: 0, 0: 0}
    # for i in range(100):
    #     print(f"Game {i}")
    #     winners[play_game()] += 1
    # print(winners)

    args = Namespace(
        numMCTSSims = 25,
        cpuct = 1.0,
    )

    game = ChessGame()

    net = ChessNetWrapper(game)
    net.load_checkpoint(os.path.join(CHESS_DIR, './checkpoints/'), 'best.pth.tar')

    mcts = MCTS(game, net, args)
    aiPlayer = lambda board: np.argmax(mcts.getActionProb(board, temp=0))

    def randomPlayer(board):
        valids = game.getValidMoves(board, 1)
        actions = np.where(valids)[0]
        return np.random.choice(actions)

    arena = Arena(aiPlayer, randomPlayer, game)
    # print(arena.playGames(10, verbose=False))

    history = get_game_history(arena)
    ChessVisualizer(history)

    pass