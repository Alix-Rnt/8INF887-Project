# 8INF887-Project
Self-supervised machine learning AI for board games.

Greatly inspired by [alpha-zero-general](https://github.com/suragnair/alpha-zero-general)

Copied files from this repo are : `Game`, `NeuralNet`, `Coach`, `MCTS` and `Arena`.

### Overview

In this repo you can find 3 games with some trained models : 
- Chess
- Checkers 6x6 and 8x8
- Pentago

You can train and test the models by yourself.

### Train

`python -m <game>.Train<Game>`

Parameters are located in the `Train<Game>.py` file in `args`:
- numIters : itraining iterations
- numEps : self-play games per iteration
- tempThreshold : move count at which the model switches from exploitation to exploration
- updateThreshold : proportion of games the model must win to be saved as 'best'
- maxlenOfQueue : maximum size for memory samples
- numMCTSSims : MCTS simulations per move
- arenaCompare : amount of games to play to compare the models
- cpuct : UCB exploitation constant

Training produces models in the `checkpoints` folder. Be careful to not erase some meaningful ones. It is also recommended to empty the folder before training.

### Test

`python -m Main --game <game> --mode <gamemode> --model_path <path>`

Games are:
- chess
- checkers6
- checkers8
- pentago

Gamemodes are:
- random : Random player VS Random Player (2 games)
- model : AI VS Random Player (10 games)
- viz : AI VS Random Player visualized on screen (1 game)
- play : Human VS AI

Model paths can be fond in the `checkpoints` folder for every game. Just put the model's name, often being `best.pth.tar`.
