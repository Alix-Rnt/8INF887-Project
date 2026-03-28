import time
import random
from tqdm import tqdm

import CheckersGame as b

def play_game(verbose=False):
    board = b.CheckersGame(10)

    round = 0
    max_rounds = 200

    while not board.is_game_over() and round < max_rounds:
        if verbose: print("\n" + "="*30)
        if verbose: print(board)
        if verbose: time.sleep(0.5)
        if verbose: print(f"It's player {board._next_player} to play")

        actions, is_capture = board.player_actions()

        if not actions:
            raise ValueError("No action available")
        
        if verbose: print(f"Available actions for player {board._next_player} :")
        if verbose: print(f"{'Capture' if is_capture else 'Move'} x{len(actions)}")

        action = random.choice(actions)
        if verbose: print(f"Chosen action : {action}")

        board.push(action, is_capture)

        round += 1

    if verbose: print("\n" + "="*30)
    if verbose: print(board)

    if round < max_rounds:
        if verbose: print(f"{board.get_winner()} won !")
        return board.get_winner()
    else:
        if verbose: print(f"Tie !")
        return 'n'

if __name__ == "__main__":
    # play_game(True)
    
    winners = {'w':0, 'b':0, 'n':0}
    for i in tqdm(range(100)):
        winners[play_game()] += 1
    print(winners)