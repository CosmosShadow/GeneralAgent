import tkinter as tk
import random

class Tetris(tk.Frame):
    BoardWidth = 10
    BoardHeight = 22
    Speed = 300
    Colors = [
        'red',
        'yellow',
        'orange',
        'green',
        'blue',
        'purple',
        'cyan'
    ]

    class Piece(object):
        Shapes = [
            [[1, 1, 1, 1]],
            [[1, 1], [1, 1]],
            [[1, 1, 0], [0, 1, 1]],
            [[0, 1, 1], [1, 1]],
            [[1, 1, 1], [0, 1, 0]],
            [[1, 1, 1], [0, 0, 1]],
            [[1, 1, 1], [1, 0, 0]]
        ]

        def __init__(self):
            self.shape = random.choice(self.Shapes)
            self.color = random.choice(Tetris.Colors)
            self.x = Tetris.BoardWidth // 2 - len(self.shape[0]) // 2
            self.y = 0

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.grid()
        self.master.title('Tetris')
        self.board = tk.Canvas(self, width=Tetris.BoardWidth * 25, height=Tetris.BoardHeight * 25, background='white')
        self.board.grid()
        self.start()

    def start(self):
        self.board.delete('all')
        self.board.create_text(Tetris.BoardWidth * 25 // 2, Tetris.BoardHeight * 25 // 2, text='Press any key to start', font=('arial', 22), fill='coral')
        self.board.bind('<Key>', self.begin)
        self.board.focus_set()

    def begin(self, event):
        self.board.delete('all')
        self.board.unbind('<Key>')
        self.score = 0
        self.board.create_text(Tetris.BoardWidth * 25 // 2, 25, text='Score: ' + str(self.score), tag='score', fill='blue', font=('arial', 22))
        self.interval = Tetris.Speed
        self.board.bind('<Up>', self.rotate)
        self.board.bind('<Down>', self.down)
        self.board.bind('<Left>', self.left)
        self.board.bind('<Right>', self.right)
        self.board.focus_set()
        self.fallingPiece = None
        self.nextPiece = Tetris.Piece()
        self.board.create_text(Tetris.BoardWidth * 25 + 50, 50, text='Next:', fill='red', font=('arial', 22))
        for i in range(len(self.nextPiece.shape)):
            for j in range(len(self.nextPiece.shape[i])):
                if self.nextPiece.shape[i][j]:
                    self.board.create_rectangle(Tetris.BoardWidth * 25 + 50 + j * 25, 75 + i * 25, Tetris.BoardWidth * 25 + 75 + j * 25, 100 + i * 25, fill=self.nextPiece.color, tag='next')
        self.gameOver = False
        self.boardData = [[0 for j in range(Tetris.BoardWidth)] for i in range(Tetris.BoardHeight)]
        self.fall()

    def fall(self):
        if self.gameOver:
            return
        if self.fallingPiece is None:
            self.fallingPiece = self.nextPiece
            self.nextPiece = Tetris.Piece()
            self.board.delete('next')
            for i in range(len(self.nextPiece.shape)):
                for j in range(len(self.nextPiece.shape[i])):
                    if self.nextPiece.shape[i][j]:
                        self.board.create_rectangle(Tetris.BoardWidth * 25 + 50 + j * 25, 75 + i * 25, Tetris.BoardWidth * 25 + 75 + j * 25, 100 + i * 25, fill=self.nextPiece.color, tag='next')
            if not self.valid():
                self.board.create_text(Tetris.BoardWidth * 25 // 2, Tetris.BoardHeight * 25 // 2, text='Game Over', fill='red', font=('arial', 22))
                self.gameOver = True
                return
        for i in range(len(self.fallingPiece.shape)):
            for j in range(len(self.fallingPiece.shape[i])):
                if self.fallingPiece.shape[i][j]:
                    self.board.create_rectangle((j + self.fallingPiece.x) * 25, (i + self.fallingPiece.y) * 25, (j + self.fallingPiece.x + 1) * 25, (i + self.fallingPiece.y + 1) * 25, fill=self.fallingPiece.color)
        self.fallingPiece.y += 1
        if not self.valid():
            self.fallingPiece.y -= 1
            self.merge()
        self.after(self.interval, self.fall)

    def valid(self):
        for i in range(len(self.fallingPiece.shape)):
            for j in range(len(self.fallingPiece.shape[i])):
                if self.fallingPiece.shape[i][j]:
                    if self.fallingPiece.x + j < 0 or self.fallingPiece.x + j >= Tetris.BoardWidth or self.fallingPiece.y + i >= Tetris.BoardHeight or self.boardData[self.fallingPiece.y + i][self.fallingPiece.x + j]:
                        return False
        return True

    def merge(self):
        for i in range(len(self.fallingPiece.shape)):
            for j in range(len(self.fallingPiece.shape[i])):
                if self.fallingPiece.shape[i][j]:
                    self.boardData[self.fallingPiece.y + i][self.fallingPiece.x + j] = self.fallingPiece.color
        self.fallingPiece = None
        self.board.delete('piece')
        self.board.delete('next')
        for i in range(Tetris.BoardHeight):
            if 0 not in self.boardData[i]:
                self.boardData.pop(i)
                self.boardData.insert(0, [0 for j in range(Tetris.BoardWidth)])
                self.score += 10
                self.board.delete('score')
                self.board.create_text(Tetris.BoardWidth * 25 // 2, 25, text='Score: ' + str(self.score), tag='score', fill='blue', font=('arial', 22))

    def rotate(self, event):
        if self.fallingPiece is None:
            return
        oldRotating = self.fallingPiece.shape
        self.fallingPiece.shape = [[oldRotating[j][i] for j in range(len(oldRotating))] for i in range(len(oldRotating[0]) - 1, -1, -1)]
        if not self.valid():
            self.fallingPiece.shape = oldRotating
        self.board.delete('piece')

    def down(self, event):
        if self.fallingPiece is None:
            return
        while self.valid():
            self.fallingPiece.y += 1
        self.fallingPiece.y -= 1
        self.merge()
        self.board.delete('piece')

    def left(self, event):
        if self.fallingPiece is None:
            return
        self.fallingPiece.x -= 1
        if not self.valid():
            self.fallingPiece.x += 1
        self.board.delete('piece')

    def right(self, event):
        if self.fallingPiece is None:
            return
        self.fallingPiece.x += 1
        if not self.valid():
            self.fallingPiece.x -= 1
        self.board.delete('piece')

if __name__ == '__main__':
    Tetris(tk.Tk()).mainloop()