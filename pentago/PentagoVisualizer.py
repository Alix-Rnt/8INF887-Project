import tkinter as tk
import numpy as np

class PentagoVisualizer:
    def __init__(self, history):
        """
        history: Liste de numpy arrays (6, 6) représentant l'état du plateau.
        """
        self.history = history
        self.current_step = 0
        self.board_size = 6
        self.cell_size = 70
        
        self.root = tk.Tk()
        self.root.title("Pentago AlphaZero Viewer")
        
        # Canvas avec un peu de marge pour la clarté
        self.canvas = tk.Canvas(self.root, 
                                width=self.board_size * self.cell_size, 
                                height=self.board_size * self.cell_size,
                                bg="#222")
        self.canvas.pack(padx=20, pady=20)
        
        # Contrôles clavier
        self.root.bind("<Right>", lambda e: self.change_step(1))
        self.root.bind("<Left>", lambda e: self.change_step(-1))
        
        self.render()
        self.root.mainloop()

    def render(self):
        self.canvas.delete("all")
        board = self.history[self.current_step]
        
        colors = ["#34495e", "#2c3e50"]

        for r in range(self.board_size):
            for c in range(self.board_size):
                quad_idx = (r // 3) * 2 + (c // 3)
                color = colors[0] if quad_idx % 2 == 0 else colors[1]
                
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#1a252f")
                
                val = board[r, c]
                if val != 0:
                    p_color = "white" if val == 1 else "black"
                    margin = 12
                    self.canvas.create_oval(x1 + margin, y1 + margin, 
                                          x2 - margin, y2 - margin, 
                                          fill=p_color, outline="#7f8c8d", width=2)

        mid = (self.board_size // 2) * self.cell_size
        self.canvas.create_line(mid, 0, mid, self.board_size * self.cell_size, fill="gold", width=4)
        self.canvas.create_line(0, mid, self.board_size * self.cell_size, mid, fill="gold", width=4)
        
        self.root.title(f"Pentago - Coup {self.current_step}/{len(self.history)-1}")

    def change_step(self, delta):
        self.current_step = max(0, min(len(self.history)-1, self.current_step + delta))
        self.render()