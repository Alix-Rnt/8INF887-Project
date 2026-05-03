import tkinter as tk
from tkinter import messagebox
import numpy as np

class PentagoGameGUI:
    def __init__(self, game, ai_player=None):
        self.game = game
        self.ai_player = ai_player
        self.board = game.getInitBoard()
        self.cur_player = 1
        
        self.selected_pos = None
        self.cell_size = 70
        self.root = tk.Tk()
        self.root.title("AlphaZero Pentago - Play")
        
        self.canvas = tk.Canvas(self.root, width=6*self.cell_size, height=6*self.cell_size, bg="#222")
        self.canvas.pack(padx=20, pady=20)
        
        self.canvas.bind("<Button-1>", self.handle_click)
        
        self.render()
        self.root.mainloop()

    def handle_click(self, event):
        if self.cur_player != 1: return
        
        col, row = event.x // self.cell_size, event.y // self.cell_size
        
        if self.selected_pos is None:
            if self.board[row, col] == 0:
                self.selected_pos = (row, col)
                self.render()
                print(f"Pawn placed at ({row},{col}). Cick on one quadrant to rotate it.")
            return

        quad_c, quad_r = col // 3, row // 3
        quadrant = quad_r * 2 + quad_c
        
        rel_x = event.x % (3 * self.cell_size)
        rotation = 0 if rel_x < (1.5 * self.cell_size) else 1

        r, c = self.selected_pos
        action = self.game._base_board.encode_action(r, c, quadrant, rotation)
        
        self.execute_move(action)
        self.selected_pos = None
        
        if self.game.getGameEnded(self.board, self.cur_player) == 0:
            self.root.after(500, self.ai_turn)

    def ai_turn(self):
        if self.ai_player:
            canon_board = self.game.getCanonicalForm(self.board, self.cur_player)
            action = self.ai_player(canon_board)
            self.execute_move(action)

    def execute_move(self, action):
        self.board, self.cur_player = self.game.getNextState(self.board, self.cur_player, action)
        self.render()
        
        res = self.game.getGameEnded(self.board, 1)
        if res != 0:
            msg = "White won !" if res == 1 else "Black won !" if res == -1 else "Draw"
            messagebox.showinfo("Game over", msg)

    def render(self):
        self.canvas.delete("all")
        for r in range(6):
            for c in range(6):
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                color = "#34495e" if ((r//3) * 2 + (c//3)) % 2 == 0 else "#2c3e50"
                
                if self.selected_pos == (r, c): color = "#e67e22"
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#1a252f")
                
                val = self.board[r, c]
                if val != 0:
                    p_color = "white" if val == 1 else "black"
                    self.canvas.create_oval(x1+12, y1+12, x2-12, y2-12, fill=p_color)

        mid = 3 * self.cell_size
        self.canvas.create_line(mid, 0, mid, 6*self.cell_size, fill="gold", width=3)
        self.canvas.create_line(0, mid, 6*self.cell_size, mid, fill="gold", width=3)