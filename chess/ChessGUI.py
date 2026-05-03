import tkinter as tk
from tkinter import messagebox
import numpy as np

DIRECTIONS_DELTAS = [(-1,-1),(-1, 0),(-1,+1),
                     ( 0,-1),        ( 0,+1),
                     (+1,-1),(+1, 0),(+1,+1)]

KNIGHT_MOVES = [(-2,-1),(-2,+1),(-1,-2),(-1,+2),
                (+1,-2),(+1,+2),(+2,-1),(+2,+1)]

PROMO_DIR = [-1, 0, 1]

class ChessGUI:
    def __init__(self, game, ai_player=None):
        self.game = game
        self.ai_player = ai_player
        self.board = game.getInitBoard()
        self.cur_player = 1
        
        self.size = 8
        self.cell_size = 70
        self.selected_square = None
        self.running = True
        
        self.pieces_icons = {
            1: {1: "♙", 2: "♖", 3: "♘", 4: "♗", 5: "♕", 6: "♔"},
            -1: {1: "♟", 2: "♜", 3: "♞", 4: "♝", 5: "♛", 6: "♚"}
        }
        
        self.root = tk.Tk()
        self.root.title("AlphaZero Chess - Play")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.canvas = tk.Canvas(self.root, width=self.size*self.cell_size, 
                               height=self.size*self.cell_size)
        self.canvas.pack()
        
        self.canvas.bind("<Button-1>", self.on_click)
        
        self.render()
        self.root.mainloop()

    def render(self):
        if not self.running: return
        self.canvas.delete("all")
        
        for r in range(self.size):
            display_r = self.size - r - 1
            for c in range(self.size):
                if self.selected_square == (r, c):
                    color = "#CCFFCC"
                else:
                    color = "#bdbdaa" if (display_r + c) % 2 == 0 else "#779556"
                
                x1, y1 = c * self.cell_size, display_r * self.cell_size
                self.canvas.create_rectangle(x1, y1, x1 + self.cell_size, y1 + self.cell_size, 
                                           fill=color, outline="")
                
                val = self.board[r, c]
                if val != 0:
                    player = 1 if val > 0 else -1
                    piece_type = abs(int(val))
                    icon = self.pieces_icons[player].get(piece_type, "?")
                    text_color = "white" if player == 1 else "black"
                    
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2,
                                          text=icon, font=("Arial", 40), fill=text_color)

    def on_click(self, event):
        if self.cur_player != 1: return 
        
        c = event.x // self.cell_size
        display_r = event.y // self.cell_size
        r = (self.size - 1) - display_r
        
        if not (0 <= r <= 7 and 0 <= c <= 7):
            return

        val = self.board[r, c]
        
        if self.selected_square is None:
            if val > 0:
                self.selected_square = (r, c)
        
        else:
            if val > 0:
                self.selected_square = (r, c)
            else:
                src_r, src_c = self.selected_square
                action = self.find_action_for_move(src_r, src_c, r, c)
                
                if action is not None:
                    self.execute_move(action)
                else:
                    self.selected_square = None
        
        self.render()

    def find_action_for_move(self, sr, sc, dr, dc):
        valids = self.game.getValidMoves(self.board, 1)
        legal_indices = np.where(valids == 1)[0]
        
        src_idx = sr * 8 + sc
        dst_idx = dr * 8 + dc

        for action in legal_indices:
            if (action // 76) == src_idx:
                move_type = action % 76
                
                if move_type < 56:
                    direction = move_type // 7
                    distance = (move_type % 7) + 1
                    dr_offset, dc_offset = DIRECTIONS_DELTAS[direction]
                    theoretical_dr = sr + dr_offset * distance
                    theoretical_dc = sc + dc_offset * distance
                elif move_type < 64:
                    dr_offset, dc_offset = KNIGHT_MOVES[move_type - 56]
                    theoretical_dr = sr + dr_offset
                    theoretical_dc = sc + dc_offset
                else:
                    dc_offset = PROMO_DIR[(move_type - 64) // 4]
                    theoretical_dr = sr + 1
                    theoretical_dc = sc + dc_offset

                if theoretical_dr == dr and theoretical_dc == dc:
                    return action
                    
        return None

    def execute_move(self, action):
        self.board, self.cur_player = self.game.getNextState(self.board, self.cur_player, action)
        self.selected_square = None
        self.render()
        
        res = self.game.getGameEnded(self.board, self.cur_player)
        if res != 0:
            self.end_game(res)
        elif self.cur_player == -1 and self.ai_player:
            self.root.after(500, self.ai_move)

    def ai_move(self):
        if not self.running: return
        canonical_board = self.game.getCanonicalForm(self.board, self.cur_player)
        action = self.ai_player(canonical_board)
        self.board, self.cur_player = self.game.getNextState(self.board, self.cur_player, action)
        self.render()
        
        res = self.game.getGameEnded(self.board, self.cur_player)
        if res != 0:
            self.end_game(res)

    def on_closing(self):
        self.running = False
        self.root.destroy()

    def end_game(self, res):
        self.running = False
        if res == 1: msg = "White won !"
        elif res == -1: msg = "Black won !"
        else: msg = "Draw !"
        messagebox.showinfo("Game over", msg)
        self.root.destroy()