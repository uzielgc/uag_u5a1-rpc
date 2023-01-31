"""
    Assigment for U5 A1: RPC.

    Author: Eloy Uziel García Cisneros (eloy.garcia@edu.uag.mx)

    usage: python rpc_server.py -s
"""

# Standard imports
import argparse
import pickle
import threading
import os
import socket
import logging

# Third-party
import pygame

# Custom
from game import Game

# Initialize parser
PARSER = argparse.ArgumentParser()

# set argument to identify if process will run as server.
PARSER.add_argument("-s", "--server", action="store_true")
ARGS = PARSER.parse_args()

# Initialize logger
logging.basicConfig(level="INFO")
LOGGER = logging.getLogger(__name__)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# window pos
os.environ["SDL_VIDEO_WINDOW_POS"] = "400,100"

ICON = pygame.image.load(os.path.join(PROJECT_DIR, "media", "yo_en_png.png"))


HOST = "127.0.0.1"
PORT = 20001

CONNECTED = False

sock = socket.socket()  # Default to TCP
sock.bind((HOST, PORT))
sock.listen(1)

CONN, ADDR = None, None


def wait_for_conn():
    global CONNECTED, CONN, ADDR

    LOGGER.info("Waiting for Player 2...")
    CONN, ADDR = sock.accept()
    CONNECTED = True
    LOGGER.info("Player connected!")
    receive()


def receive():
    while True:
        # Wait for data from client.
        data = CONN.recv(1024)
        data = pickle.loads(data)
        gato.turn = True
        if data.get("reset"):
            gato.reset()
        else:
            gato.set_cell_value(data["x"], data["y"], "o")


if __name__ == "__main__":
    """Control process workflow."""

    # Start socket receiver in thread.
    Game.create_thread(wait_for_conn)

    # Game runing in main thread.
    player = "x" if ARGS.server else "o"

    surface = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Gato")
    pygame.display.set_icon(ICON)

    gato = Game(player=player)

    IS_IT_RUNNING = True

    while IS_IT_RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                IS_IT_RUNNING = False

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and CONNECTED
                and gato.turn
                and not gato.game_over()
            ):
                pos = pygame.mouse.get_pos()
                x, y = pos[0] // 200, pos[1] // 200
                gato.get_mouse(x, y)

                data = {"x": x, "y": y}
                data = pickle.dumps(data)

                # Sends data to client.
                CONN.send(data)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("RESET!")
                    gato.reset()
                    data = {"reset": True}
                    data = pickle.dumps(data)

                    CONN.send(data)
                elif event.key == pygame.K_ESCAPE:
                    IS_IT_RUNNING = False

        surface.fill((0, 0, 0))

        gato.draw(surface=surface)
        pygame.display.flip()
