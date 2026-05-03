import tkinter as tk
from tkinter import messagebox
import numpy as np

class CheckersGUI:
    def __init__(self, game, ai_player=None):
        self.game = game
        self.ai_player = ai_player
        self.board = game.getInitBoard()
        self.cur_player = 1
        
        self.size = game.size 
        self.cell_size = 60
        self.selected_square = None
        
        self.root = tk.Tk()
        self.root.title("AlphaZero Checkers - Play")
        
        self.canvas = tk.Canvas(self.root, width=self.size*self.cell_size, 
                               height=self.size*self.cell_size)
        self.canvas.pack()
        
        self.canvas.bind("<Button-1>", self.on_click)
        
        self.render()
        self.root.mainloop()

    def render(self):
        self.canvas.delete("all")
        pieces = self.board[:-1]
        progress = self.board[-1, 0]
        
        for r in range(self.size):
            for c in range(self.size):
                if self.selected_square == (r, c):
                    color = "#CCFFCC"
                else:
                    color = "#DDBB99" if (r + c) % 2 == 0 else "#664422"
                
                self.canvas.create_rectangle(c*self.cell_size, r*self.cell_size, 
                                           (c+1)*self.cell_size, (r+1)*self.cell_size, 
                                           fill=color, outline="")
                
                val = pieces[r, c]
                if val != 0:
                    p_color = "white" if val > 0 else "black"
                    outline = "gold" if abs(val) == 2 else "grey"
                    
                    self.canvas.create_oval(c*self.cell_size+10, r*self.cell_size+10, 
                                          (c+1)*self.cell_size-10, (r+1)*self.cell_size-10, 
                                          fill=p_color, outline=outline, width=3)
        
        self.root.title(f"Joueur: {'Blanc' if self.cur_player == 1 else 'Noir'} - Progrès: {int(progress)}")

    def on_click(self, event):
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        
        if r >= self.size or c >= self.size: return

        val = self.board[r, c]
        
        if self.selected_square is None:
            if (val * self.cur_player) > 0:
                self.selected_square = (r, c)
        else:
            src_r, src_c = self.selected_square
            action = (src_r * self.size + src_c) * (self.size**2) + (r * self.size + c)
            
            valids = self.game.getValidMoves(self.board, self.cur_player)
            if valids[action]:
                self.execute_move(action)
            else:
                if (val * self.cur_player) > 0:
                    self.selected_square = (r, c)
                else:
                    self.selected_square = None
        
        self.render()

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
        canonical_board = self.game.getCanonicalForm(self.board, self.cur_player)
        action = self.ai_player(canonical_board)
        self.board, self.cur_player = self.game.getNextState(self.board, self.cur_player, action)
        self.render()
        
        res = self.game.getGameEnded(self.board, self.cur_player)
        if res != 0:
            self.end_game(res)

    def end_game(self, res):
        if res == 1: msg = "White won !"
        elif res == -1: msg = "Black won !"
        else: msg = "Draw !"
        messagebox.showinfo("Game Over", msg)
        self.root.destroy()