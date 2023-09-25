```python
import tkinter as tk
import random

class Tetris(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tetris")
        self.geometry("200x400")
        self.canvas = tk.Canvas(self, bg='white', width=200, height=400)
        self.canvas.pack()
        self.shapes = [
            [[1, 1, 1, 1]],
            [[1, 1], [1, 1]],
            [[1, 1, 0], [0, 1, 1]],
            [[0, 1, 1], [1, 1]],
            [[1, 1, 1], [0, 1, 0]],
            [[1, 1, 1], [0, 0, 1]],
            [[1, 1, 1], [1, 0, 0]]
        ]
        self.current_shape = random.choice(self.shapes)
        self.current_position = [0, 0]
        self.board = [[0]*10 for _ in range(20)]
        self.game_over = False
        self.score = 0
        self.start()

    def start(self):
        self.canvas.after(1000, self.move_down)

    def move_down(self):
        if not self.game_over:
            self.current_position[1] += 1
            if self.check_collision():
                self.current_position[1] -= 1
                self.add_to_board()
                self.check_lines()
                self.current_shape = random.choice(self.shapes)
                self.current_position = [0, 0]
                if self.check_collision():
                    self.game_over = True
            self.draw()
            self.canvas.after(1000, self.move_down)

    def check_collision(self):
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                try:
                    if cell and self.board[y+self.current_position[1]][x+self.current_position[0]]:
                        return True
                except IndexError:
                    return True
        return False

    def add_to_board(self):
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.board[y+self.current_position[1]][x+self.current_position[0]] = 1

    def check_lines(self):
        for y, row in enumerate(self.board):
            if all(row):
                del self.board[y]
                self.board = [[0]*10] + self.board
                self.score += 1

    def draw(self):
        self.canvas.delete('all')
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    self.canvas.create_rectangle(x*20, y*20, (x+1)*20, (y+1)*20, fill='black')
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.canvas.create_rectangle((x+self.current_position[0])*20, (y+self.current_position[1])*20, (x+self.current_position[0]+1)*20, (y+self.current_position[1]+1)*20, fill='black')

if __name__ == "__main__":
    game = Tetris()
    game.mainloop()
```