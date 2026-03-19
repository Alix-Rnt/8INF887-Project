import random
import time
import pygame
import math

import CHGame as b
import Action as a

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

    while not board.is_game_over():
        if verbose: print("\n" + "="*30)
        if verbose: print(board)

        actions = board.player_actions()

        if not actions:
            raise ValueError("No action available")
        
        if verbose: print(f"Available actions for player {board._next_player._name} :")
        for action in actions:
            if verbose: display_action(action)

        random_action = random.choice(actions)
        if verbose: print("Choice : ")
        if verbose: display_action(random_action)
        board.push(random_action)

        # time.sleep(1)

    winner = board.get_winner()

    if verbose: print("\n" + "="*30)
    if verbose: print(board)
    if verbose: print("rounds :", round)
    if verbose: print(winner._name, "won")
    return winner._name

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

def display_game(verbose=False):
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()

    board = b.HexBoard()
        
    display_board(screen, board)

    pygame.display.flip()
    clock.tick(60)

    waiting_time = 0
    cooldown = time.time()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ############
        # GAME LOGIC
        ############

        if not board.is_game_over():
            if time.time() - cooldown >= waiting_time:
                actions = board.player_actions()

                if not actions:
                    raise ValueError("No action available")
                
                if verbose: print(f"Available actions for player {board._next_player._name} :")
                for action in actions:
                    if verbose: display_action(action)

                random_action = random.choice(actions)
                if verbose: print("Choice : ")
                if verbose: print(board._next_player._name)
                if verbose: display_action(random_action)
                board.push(random_action)

                cooldown = time.time()
        else:
            winner = board.get_winner()
            if winner == None: print("Draw")
            else: print(board.get_winner()._name, "won")
            time.sleep(1)
            break

        ###############
        # DISPLAY LOGIC
        ###############
        
        display_board(screen, board)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    # winners = {"P1":0, "P2":0}
    # for _ in range(10):
    #     winners[play_game()] += 1
    # print(winners)
    display_game(True)
    # play_game(False)
    pass