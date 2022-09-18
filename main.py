import math
import threading
import pygame


###
LIMIT_FPS = False
###

pygame.init()

WIDTH = 800
HEIGHT = 800

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Solver")

font = pygame.font.SysFont("calibri", 50, True)

clock = pygame.time.Clock()


class Board:
    def __init__(self):
        self.board = [([0] * 9) for _ in range(9)]
        self.fixed_points = []
        self.selected = (-1, -1)
        self.change = True

        self.cell_width = WIDTH / len(self.board)
        self.cell_height = HEIGHT / len(self.board)

    def draw_grid(self, win):
        n = len(self.board)
        if self.selected[0] > -1:
            pygame.draw.rect(win, (220, 220, 220),
                             (self.selected[1] * self.cell_width, self.selected[0] * self.cell_height,
                              self.cell_width, self.cell_height))
        for i in range(n):
            pygame.draw.line(win, '#000000', (self.cell_width * i, 0),
                             (self.cell_width * i, HEIGHT),
                             2 if i % int(math.sqrt(n)) == 0 else 1)
            pygame.draw.line(win, '#000000', (0, self.cell_height * i), (WIDTH, self.cell_height * i),
                             2 if i % int(math.sqrt(n)) == 0 else 1)

        pygame.draw.line(win, '#000000', (WIDTH - 2, 0), (WIDTH - 2, HEIGHT), 2)
        pygame.draw.line(win, '#000000', (0, HEIGHT - 2), (WIDTH, HEIGHT - 2), 2)

    def draw_numbers(self, win):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                text = font.render(f'{"" if self.board[r][c] == 0 else self.board[r][c]}', True,
                                   "#ff0000" if (r, c) in self.fixed_points else '#000000')
                win.blit(text, (self.cell_width * c + self.cell_width / 2 - text.get_width() / 2,
                                self.cell_height * r + self.cell_height / 2 - text.get_height() / 2))

    def change_selection(self, x, y):
        self.selected = int(y // self.cell_height), int(x // self.cell_width)

    def change_cell(self, num):
        if self.selected[0] > -1:
            if num == 0:
                self.fixed_points.remove(self.selected)
            else:
                self.fixed_points.append(self.selected)
            self.board[self.selected[0]][self.selected[1]] = num

    def get_chunk(self, r, c):
        return r // math.floor(math.sqrt(len(self.board))), c //  math.floor(math.sqrt(len(self.board)))

    def is_legit(self, r, c):
        if self.board[r][c] == 0:
            return True

        for i in range(len(self.board)):
            if self.board[r][c] == self.board[i][c] and r != i:
                return False

            if self.board[r][c] == self.board[r][i] and c != i:
                return False

        chunk = self.get_chunk(r, c)
        for row in range(chunk[0] * math.floor(math.sqrt(len(self.board))),  (chunk[0]+1) * math.floor(math.sqrt(len(self.board)))):
            for col in range(chunk[1] * math.floor(math.sqrt(len(self.board))),
                             (chunk[1] + 1) * math.floor(math.sqrt(len(self.board)))):
                if self.board[row][col] == self.board[r][c] and r != row and c != col:
                    return False

        return True


def manual_fill(b: Board):
    x, y = pygame.mouse.get_pos()

    if pygame.mouse.get_pressed()[0] and b.change:
        b.change_selection(x, y)


def next_cell(r, c, b):
    c += 1
    if c >= len(b.board):
        r += 1
        c = 0

    while (r, c) in b.fixed_points:
        c += 1
        if c >= len(b.board):
            r += 1
            c = 0

    return r, c


def solve_ext(b: Board):
    start = 0, 0
    while start in b.fixed_points:
        start = next_cell(start[0], start[1], b)

    solve(b, start[0], start[1])
    print("solved!")


def solve(b: Board, r, c):
    if LIMIT_FPS:
        pygame.time.delay(10)
    if r >= len(b.board):
        return True

    b.board[r][c] += 1
    while not b.is_legit(r, c):
        b.board[r][c] += 1
        if b.board[r][c] > 9:
            b.board[r][c] = 0
            return False

    next_r, next_c = next_cell(r, c, b)

    while not solve(b, next_r, next_c):
        b.board[r][c] += 1
        if b.board[r][c] > 9:
            b.board[r][c] = 0
            return False

        while not b.is_legit(r, c):
            b.board[r][c] += 1
            if b.board[r][c] > 9:
                b.board[r][c] = 0
                return False

        next_r, next_c = next_cell(r, c, b)

    return True


board = Board()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if 48 <= event.key <= 57 and board.change:
                board.change_cell(int(chr(event.key)))
            if event.key == pygame.K_RETURN and board.change:
                board.change = False
                board.selected = (-1, -1)
                threading.Thread(target=solve_ext, args=(board, )).start()

    WIN.fill('#ffffff')
    board.draw_grid(WIN)
    board.draw_numbers(WIN)
    manual_fill(board)
    pygame.display.update()
    if LIMIT_FPS:
        clock.tick(30)
