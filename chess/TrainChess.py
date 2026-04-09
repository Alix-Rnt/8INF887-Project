import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from argparse import Namespace

from Game import Game
from Coach import Coach
from .ChessGame import ChessGame
from .ChessNet import ChessNetWrapper

args = Namespace(
    numIters          = 100,   # nombre d'itérations d'entraînement
    numEps            = 50,    # parties de self-play par itération
    tempThreshold     = 15,    # après ce nombre de coups, temp → 0
    updateThreshold   = 0.55,  # seuil pour accepter le nouveau réseau
    maxlenOfQueue     = 200000,# taille max de la mémoire d'exemples
    numMCTSSims       = 25,    # simulations MCTS par coup
    arenaCompare      = 20,    # parties pour comparer les deux réseaux
    cpuct             = 1.0,   # constante d'exploration UCB

    checkpoint        = './checkpoints/',
    load_model        = False,
    load_folder_file  = ('./checkpoints/', 'best.pth.tar'),
    numItersForTrainExamplesHistory = 20,
)

if __name__ == '__main__':
    game = ChessGame()
    net = ChessNetWrapper(game)

    if args.load_model:
        net.load_checkpoint(*args.load_folder_file)

    coach = Coach(game, net, args)
    coach.learn()