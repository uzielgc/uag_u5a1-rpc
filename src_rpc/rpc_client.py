"""
    Assigment for U5 A1: RPC.

    Author: Eloy Uziel García Cisneros (eloy.garcia@edu.uag.mx)

    usage: python rpc_client.py [-s]
"""

# Standard imports
import threading
import pygame
import argparse

# Third-party
import grpc

# Custom
import gato_pb2 as gato
import gato_pb2_grpc as rpc

from game import Game

address = "localhost"
port = 20001

# Initialize parser
PARSER = argparse.ArgumentParser()
# set argument to identify if process will run as message broker.
PARSER.add_argument("-s", "--server", action="store_true")
ARGS = PARSER.parse_args()

ICON = pygame.image.load("/Users/uzielgc/Documents/personal/yo_en_png.png")


class Client:
    def __init__(self, player):
        self.player = player
        self.game = Game(player=player)
        # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ":" + str(port))
        self.conn = rpc.GatoServerStub(channel)
        # create new listening thread for when new message streams come in
        threading.Thread(target=self.__listen_for_messages, daemon=True).start()

    def __listen_for_messages(self):
        """
        This method will be ran in a separate thread as the main/ui thread, because the for-in call is blocking
        when waiting for new messages
        """
        for move in self.conn.RecordMove(
            gato.Empty()
        ):  # this line will wait for new messages from the server!
            if move.player != self.player:
                self.game.turn = True
                self.game.set_cell_value(int(move.x), int(move.y), move.player)

    def send_message(self, data):
        """
        This method is called when user enters something into the textbox
        """
        if data:
            move = gato.Move()
            move.player = data["player"]
            move.x = str(data["x"])
            move.y = str(data["y"])
            self.conn.MakeMove(move)


if __name__ == "__main__":
    player = "x" if ARGS.server else "o"
    client = Client(
        player
    )  # this starts a client and thus a thread which keeps connection to server open

    surface = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Gato")
    pygame.display.set_icon(ICON)

    # gato = Game(player=player)

    IS_IT_RUNNING = True

    while IS_IT_RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                IS_IT_RUNNING = False

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and client.game.turn
                and not client.game.game_over()
            ):
                pos = pygame.mouse.get_pos()
                x, y = pos[0] // 200, pos[1] // 200
                client.game.get_mouse(x, y)

                data = {"x": x, "y": y, "player": client.player}

                client.send_message(data)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("RESET!")
                    # gato.reset()
                    data = {"reset": True}
                    # data = pickle.dumps(data)

                    # CONN.send(data)
                elif event.key == pygame.K_ESCAPE:
                    IS_IT_RUNNING = False

        surface.fill((0, 0, 0))

        client.game.draw(surface=surface)
        pygame.display.flip()
