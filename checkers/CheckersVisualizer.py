import tkinter as tk

class CheckersVisualizer:
    def __init__(self, history):
        self.history = history
        self.current_step = 0
        self.size = history[0].shape[0] - 1
        self.cell_size = 60
        
        self.root = tk.Tk()
        self.root.title("AlphaZero Checkers Viewer")
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
                # Board
                color = "#DDBB99" if (r + c) % 2 == 0 else "#664422"
                self.canvas.create_rectangle(c*self.cell_size, r*self.cell_size, 
                                           (c+1)*self.cell_size, (r+1)*self.cell_size, 
                                           fill=color)
                
                # Pieces
                val = board[r, c]
                if val != 0:
                    p_color = "white" if val > 0 else "black"
                    outline = "gold" if abs(val) == 2 else "grey"
                    self.canvas.create_oval(c*self.cell_size+10, r*self.cell_size+10, 
                                          (c+1)*self.cell_size-10, (r+1)*self.cell_size-10, 
                                          fill=p_color, outline=outline, width=3)
        
        self.root.title(f"Coup {self.current_step}/{len(self.history)-1} - Progress: {board[-1,0]}")

    def change_step(self, delta):
        self.current_step = max(0, min(len(self.history)-1, self.current_step + delta))
        self.render()