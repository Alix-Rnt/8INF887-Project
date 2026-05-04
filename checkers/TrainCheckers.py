import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from argparse import Namespace

from Coach import Coach
from .CheckersGame import CheckersGame
from .CheckersNet import CheckersNetWrapper

CHECKERS_DIR = os.path.dirname(os.path.abspath(__file__))

args = Namespace(
    # numIters        = 100,    # nombre d'itérations d'entraînement
    # numEps          = 50,     # parties de self-play par itération
    # tempThreshold   = 15,     # après ce nombre de coups, temp = 0
    # updateThreshold = 0.55,   # seuil pour accepter le nouveau réseau
    # maxlenOfQueue   = 200000, # taille max de la mémoire d'exemples
    # numMCTSSims     = 25,     # simulations MCTS par coup
    # arenaCompare    = 20,     # parties pour comparer les deux réseaux
    # cpuct           = 1.0,    # constante d'exploration UCB

    numIters        = 50,
    numEps          = 50,
    tempThreshold   = 15,
    updateThreshold = 0.55,
    maxlenOfQueue   = 200000,
    numMCTSSims     = 25,
    arenaCompare    = 20,
    cpuct           = 1.0,

    checkpoint = os.path.join(CHECKERS_DIR, './checkpoints/'),
    load_model  = False,
    load_folder_file = (os.path.join(CHECKERS_DIR, './checkpoints/'), 'best.pth.tar'),
    numItersForTrainExamplesHistory = 20,
)

if __name__ == '__main__':
    game = CheckersGame(8)
    net = CheckersNetWrapper(game)

    if args.load_model:
        net.load_checkpoint(*args.load_folder_file)

    coach = Coach(game, net, args)

    start = time.time()
    coach.learn()

    print(f"Total time : {time.time() - start:.1f}s")