import tkinter as tk

class ChessVisualizer:
    def __init__(self, history):
        self.history = history
        self.current_step = 0
        self.size = 8
        self.cell_size = 70
        
        self.pieces_icons = {
            1: {1: "♙", 2: "♖", 3: "♘", 4: "♗", 5: "♕", 6: "♔"}, # White
            -1: {1: "♟", 2: "♜", 3: "♞", 4: "♝", 5: "♛", 6: "♚"}  # Black
        }
        
        self.root = tk.Tk()
        self.root.title("AlphaZero Chess Viewer")
        self.canvas = tk.Canvas(self.root, width=self.size*self.cell_size, 
                               height=self.size*self.cell_size)
        self.canvas.pack()
        
        self.root.bind("<Right>", lambda e: self.change_step(1))
        self.root.bind("<Left>", lambda e: self.change_step(-1))
        
        self.render()
        self.root.mainloop()

    def render(self):
        self.canvas.delete("all")
        board = self.history[self.current_step]
        
        for r in range(self.size):
            for c in range(self.size):
                color = "#bdbdaa" if (r + c) % 2 == 0 else "#779556"
                self.canvas.create_rectangle(c*self.cell_size, r*self.cell_size, 
                                           (c+1)*self.cell_size, (r+1)*self.cell_size, 
                                           fill=color, outline="")
                
                val = board[self.size - r - 1, c]
                if val != 0:
                    player = 1 if val > 0 else -1
                    piece_type = abs(int(val))
                    
                    icon = self.pieces_icons[player].get(piece_type, "?")
                    
                    text_color = "white" if player == 1 else "black"
                    
                    self.canvas.create_text(c*self.cell_size + self.cell_size/2, 
                                          r*self.cell_size + self.cell_size/2,
                                          text=icon, font=("Arial", 40), fill=text_color)
        
        self.root.title(f"Échecs - Coup {self.current_step}/{len(self.history)-1}")

    def change_step(self, delta):
        self.current_step = max(0, min(len(self.history)-1, self.current_step + delta))
        self.render()