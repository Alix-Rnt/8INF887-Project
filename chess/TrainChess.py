import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from argparse import Namespace

from Coach import Coach
from .ChessGame import ChessGame
from .ChessNet import ChessNetWrapper

CHESS_DIR = os.path.dirname(os.path.abspath(__file__))

args = Namespace(
    # numIters        = 100,    # nombre d'itérations d'entraînement
    # numEps          = 50,     # parties de self-play par itération
    # tempThreshold   = 15,     # après ce nombre de coups, temp = 0
    # updateThreshold = 0.55,   # seuil pour accepter le nouveau réseau
    # maxlenOfQueue   = 200000, # taille max de la mémoire d'exemples
    # numMCTSSims     = 25,     # simulations MCTS par coup
    # arenaCompare    = 20,     # parties pour comparer les deux réseaux
    # cpuct           = 1.0,    # constante d'exploration UCB

    numIters        = 5,
    numEps          = 5,
    tempThreshold   = 15,
    updateThreshold = 0.4,
    maxlenOfQueue   = 1000,
    numMCTSSims     = 5,
    arenaCompare    = 6,
    cpuct           = 1.0,

    checkpoint = os.path.join(CHESS_DIR, './checkpoints/'),
    load_model  = False,
    load_folder_file = (os.path.join(CHESS_DIR, './checkpoints/'), 'best.pth.tar'),
    numItersForTrainExamplesHistory = 2,
)

if __name__ == '__main__':
    game = ChessGame()
    net = ChessNetWrapper(game)

    if args.load_model:
        net.load_checkpoint(*args.load_folder_file)

    coach = Coach(game, net, args)

    start = time.time()
    coach.learn()
    print(f"Total time : {time.time() - start:.1f}s")