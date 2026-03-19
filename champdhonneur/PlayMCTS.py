import pygame
import math
import random

import CHGame as b
import Action as a
from MCTSNode import mcts_search

def display_action(action):
    match action[0]:
        case a.Action.FORCE_PASS:
            print(f"{action[0].name}")
        case a.Action.PASS:
            print(f"{action[0].name}")
        case a.Action.RECRUIT:
            print(f"{action[0].name}")
        case a.Action.SUMMON:
            print(f"{action[0].name} at {action[1]}")
        case a.Action.MOVE:
            print(f"{action[0].name} from {action[1]} to {action[2]}")
        case a.Action.ATTACK:
            print(f"{action[0].name} from {action[1]} to {action[2]}")
        case a.Action.CAPTURE:
            print(f"{action[0].name} at {action[1]}")

def play_game(verbose=False):
    board = b.HexBoard()

    print("MCTS Champ d'Honneur Demo")

    while not board.is_game_over():
        if verbose: print("\n" + "="*30)
        if verbose: print(board)

        current_player = board._next_player

        if current_player == board._players[0]:
            move = mcts_search(board, iterations=500)
            if verbose: print(f"MCTS plays: {move}")
        else:
            # time.sleep(1) # some time to see ia action
            empty = board.player_actions()
            move = random.choice(empty)
            # move = [(a.Action.PASS,)] # force random to skip
            if verbose: print(f"Random plays: {move}")

        board.push(move)
        # time.sleep(0.5)

    winner = board.get_winner()
    if verbose: print(board)
    if winner:
        print(f"Player {winner._name} wins!")
    else:
        print("Draw")

# Pygame display
screen_size = (600, 600)
center_screen = (300, 300)
hex_radius = 30
city_radius = 23
unit_radius = 18

def format_coord(coord):
    x = ((coord[0] - 3) * (1 + math.sin(math.pi/6))) * hex_radius + center_screen[0]
    y = ((3 - coord[1]) * math.sqrt(3) - (coord[0] - 3) * math.cos(math.pi/6)) * hex_radius + center_screen[1]
    return ((x,y))

def get_hexagon_points(center, size):
    points = []
    for i in range(6):
        angle_rad = math.radians(60 * i)
        x = center[0] + size * math.cos(angle_rad)
        y = center[1] + size * math.sin(angle_rad)
        points.append((x, y))
    return points

def display_board(screen: pygame.Surface, board: b.HexBoard):
    screen.fill((200, 200, 200))

    # board
    for i, pos in enumerate(board.board.keys()):
        points = get_hexagon_points(format_coord(pos), hex_radius)
        color = (100, 100, 100)
        
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 2)

    # cities
    for i, pos in enumerate(board._cities):
        center = format_coord(pos)

        color = (0, 0, 0)

        if (pos in board._get_player_cities(board._players[0])):
            color = (0, 0, 255)
        elif (pos in board._get_player_cities(board._players[1])):
            color = (255, 0, 0)
        else:
            color = (0, 255, 127)

        pygame.draw.circle(screen, color, center, city_radius)
        pygame.draw.circle(screen, (0, 0, 0), center, city_radius, 1)

    # units
    for i, pos in enumerate(board._get_player_units(board._players[0])):
        center = format_coord(pos)
        color = (120, 120, 255)

        pygame.draw.circle(screen, color, center, unit_radius)
        pygame.draw.circle(screen, (0, 0, 0), center, unit_radius, 1)
    for i, pos in enumerate(board._get_player_units(board._players[1])):
        center = format_coord(pos)
        color = (255, 120, 120)

        pygame.draw.circle(screen, color, center, unit_radius)
        pygame.draw.circle(screen, (0, 0, 0), center, unit_radius, 1)

    # player info
    font = pygame.font.SysFont("Arial", 24, bold=True)
    # P1
    player1 = board._players[0]
    label = f"Player{player1._name} : SIDE = {player1.units_side}, BAG = {player1.units_bag}, HAND = {player1.units_hand}, USED = {player1.units_used}"
    text_surf = font.render(label, True, (255, 255, 0))
    text_rect = text_surf.get_rect(bottomleft=(0, 600))
    screen.blit(text_surf, text_rect)

    # P2
    player2 = board._players[1]
    label = f"Player{player2._name} : SIDE = {player2.units_side}, BAG = {player2.units_bag}, HAND = {player2.units_hand}, USED = {player2.units_used}"
    text_surf = font.render(label, True, (255, 255, 0))
    text_rect = text_surf.get_rect(topleft=(0, 0))
    screen.blit(text_surf, text_rect)

def clic_listener(screen, board):
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass

# Play against MCTS
def display_game(verbose=False):
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()

    board = b.HexBoard()
        
    display_board(screen, board)

    pygame.display.flip()
    clock.tick(60)

    waiting_time = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ############
        # GAME LOGIC
        ############

        if not board.is_game_over():
            actions = board.player_actions()

            if not actions:
                raise ValueError("No action available")
            
            if verbose: print(f"Available actions for player {board._next_player._name} :")
            for action in actions:
                if verbose: display_action(action)

            # if (board._next_player == board._players[0]):
            #     while action == None:
            #         action = clic_listener(screen, board)
            # else:
            #     action = mcts_search(board, 1000)

            if (board._next_player == board._players[0]):
                action = mcts_search(board, 200)
                print(len(board._get_player_cities(board._next_player)))
            else:
                action = random.choice(actions)


            if verbose: print("Choice : ")
            if verbose: print(board._next_player._name)
            if verbose: display_action(action)

            board.push(action)

        else:
            winner = board.get_winner()
            if winner == None: print("Draw")
            else: print(board.get_winner()._name, "won")
            break

        ###############
        # DISPLAY LOGIC
        ###############
        
        display_board(screen, board)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    display_game(False)
    pass