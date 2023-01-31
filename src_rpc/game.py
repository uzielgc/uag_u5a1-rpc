import pygame
import tabulate
import logging

import threading


from typing import Union


LOGGER = logging.getLogger(__name__)


class Game:

    WINNERS = (
        [(0, 0), (0, 1), (0, 2)],  # Horizontal
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        [(0, 0), (1, 0), (2, 0)],  # Vertical
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        [(0, 0), (1, 1), (2, 2)],  # Diagonal
        [(0, 2), (1, 1), (2, 0)],
    )

    def __init__(self, player) -> None:
        

        self.grid_lines = [
            ((0, 200), (600, 200)),
            ((0, 400), (600, 400)),
            ((200, 0), (200, 600)),
            ((400, 0), (400, 600)),
        ]

        self.grid = self._reset_grid()

        # self.net = None
        # self.init_player(player=player)


        self.winner = None
        self.player = player
        self.turn = self.player == 'x' # 'Server always X, go first
        self.moves = 0

        LOGGER.info('You are %s, ', player)

        pygame.font.init()

        self.font = pygame.font.SysFont("Helvetica", 250)
        self.p_x = self.font.render("X", False, (200, 200, 200))
        self.p_o = self.font.render("O", False, (200, 200, 200))

        LOGGER.info("X STARTS!")
    
    @staticmethod
    def create_thread(target):
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
    
    # def init_player(self, player):
    #     if player == 'x':
    #         # X is server
    #         self.net = Server() 
    #         self.create_thread(self.net.start_server)
    #     else:
    #         self.net = Client()
    #         self.net.connect()
    #         self.create_thread(self.net.receive)


    def draw(self, surface):
        for line in self.grid_lines:
            pygame.draw.line(
                surface=surface,
                color=(200, 200, 200),
                start_pos=line[0],
                end_pos=line[1],
            )

        for y, line in enumerate(self.grid):
            for x, mark in enumerate(line):
                if mark == "o":
                    surface.blit(self.p_o, (x * 200, y * 200))
                elif mark == "x":
                    surface.blit(self.p_x, (x * 200, y * 200))

    def get_cell_value(self, x, y):
        return self.grid[y][x]

    def set_cell_value(self, x, y, value):
        self.moves += 1
        self.grid[y][x] = value
        self.won(value)

    def get_mouse(self, x, y):
        if self.get_cell_value(x, y) != 0:
            return

        #self.moves += 1
        self.set_cell_value(x, y, self.player)
        
        
        self.next_turn()

    def next_turn(self):
        self.turn = False

    def game_over(self):
        return self.winner is not None

    def won(self, player):
        for indexes in self.WINNERS:
            row = [self.grid[r][c] for r, c in indexes]
            if all(cell == player for cell in row):
                LOGGER.info("%s WINS!", player)
                self.winner = player
        if self.moves >= 9:
            self.winner = 'EMPATE'
            LOGGER.info("GG, Empate")


    @staticmethod
    def _reset_grid():
        return [[0 for x in range(3)] for y in range(3)]

    def reset(self):
        self.winner = None
        self.grid = self._reset_grid()
        self.moves = 0

        msg = 'YOUR TURN!' if self.turn else 'Wait for move!'
        LOGGER.info(msg)

    def pring_grid(self):
        print(tabulate.tabulate(self.grid))


