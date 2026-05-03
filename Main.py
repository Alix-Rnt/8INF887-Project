import sys
import argparse
import numpy as np
from Arena import Arena
from MCTS import MCTS
from Players import RandomPlayer

from chess.ChessGame import ChessGame
from chess.ChessNet import ChessNetWrapper
from chess.ChessVisualizer import ChessVisualizer
from chess.ChessGUI import ChessGUI

from checkers.CheckersGame import CheckersGame
from checkers.CheckersNet import CheckersNetWrapper
from checkers.CheckersVisualizer import CheckersVisualizer
from checkers.CheckersGUI import CheckersGUI

from pentago.PentagoGame import PentagoGame
from pentago.PentagoNet import PentagoNetWrapper
from pentago.PentagoVisualizer import PentagoVisualizer
from pentago.PentagoGameUI import PentagoGameGUI

def get_game_history(arena):
    board = arena.game.getInitBoard()
    history = [board.copy()]
    curPlayer = 1
    
    print("Loading game...")
    while arena.game.getGameEnded(board, curPlayer) == 0:
        action = arena.player1(arena.game.getCanonicalForm(board, curPlayer)) if curPlayer == 1 \
                 else arena.player2(arena.game.getCanonicalForm(board, curPlayer))
        
        board, curPlayer = arena.game.getNextState(board, curPlayer, action)
        history.append(board.copy())
        
    return history

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Game Models and Visualization')
    parser.add_argument('--game', choices=['chess', 'checkers6', 'checkers8', 'pentago'],
                        help='chess: Chess game (not performant), checkers6: Checkers 6x6, ' \
                        'checkers8: Checkers 8x8, pentago: Pentago game')
    parser.add_argument('--mode', choices=['random', 'model', 'viz', 'play'], default='random',
                        help='random: Random vs Random, model: Arena, viz: Visualisation, play: Human play against AI')
    parser.add_argument('--model_path', type=str, default='best.pth.tar')
    args = parser.parse_args()

    game, nnet, path, viz, gui = None, None, '', None, None

    # Chose game, neural network, folder path, visualizer and GUI
    if args.game == 'chess':
        # if args.mode == 'play':
        #     print("Not implemented")
        #     sys.exit()
        game = ChessGame()
        nnet = ChessNetWrapper(game)
        path = 'chess'
        viz = ChessVisualizer
        gui = ChessGUI

    elif args.game == 'checkers6':
        game = CheckersGame(6)
        nnet = CheckersNetWrapper(game)
        path = 'checkers'
        viz = CheckersVisualizer
        gui = CheckersGUI

    elif args.game == 'checkers8':
        game = CheckersGame(8)
        nnet = CheckersNetWrapper(game)
        path = 'checkers'
        viz = CheckersVisualizer
        gui = CheckersGUI

    elif args.game == 'pentago':
        game = PentagoGame()
        nnet = PentagoNetWrapper(game)
        path = 'pentago'
        viz = PentagoVisualizer
        gui = PentagoGameGUI
    
    else:
        pass

    print(f"=== Play {args.game} ===")

    # Chose mode
    if args.mode == 'random':
        print("Mode: Random vs Random")
        random_player = RandomPlayer(game, 1).play
        arena = Arena(random_player, random_player, game)
        print(arena.playGames(2))

    elif args.mode == 'model':
        print(f"Mode: Model {args.model_path} (WHITE) vs Random (BLACK)")
        nnet.load_checkpoint(path + './checkpoints/', args.model_path)

        mcts = MCTS(game, nnet, argparse.Namespace(numMCTSSims=50, cpuct=1.0))
        model_player = lambda x: np.argmax(mcts.getActionProb(x, temp=0))
        random_player = RandomPlayer(game).play

        arena = Arena(model_player, random_player, game)
        print(arena.playGames(10))
    
    elif args.mode == 'viz':
        print(f"Mode: Model {args.model_path} (WHITE) vs visualization Random (BLACK)")
        print("Use LEFT and RIGHT to move backward or forward in the game")
        nnet.load_checkpoint(path + './checkpoints/', args.model_path)

        mcts = MCTS(game, nnet, argparse.Namespace(numMCTSSims=50, cpuct=1.0))
        model_player = lambda x: np.argmax(mcts.getActionProb(x, temp=0))
        random_player = RandomPlayer(game).play

        arena = Arena(model_player, random_player, game)
        history = get_game_history(arena)

        viz(history)

    elif args.mode == 'play':
        nnet.load_checkpoint(path + './checkpoints/', args.model_path)

        mcts = MCTS(game, nnet, argparse.Namespace(numMCTSSims=50, cpuct=1.0))
        model_player = lambda x: np.argmax(mcts.getActionProb(x, temp=0))
        
        gui(game, model_player)