"""
    Assigment for U5 A1: RPC.

    Author: Eloy Uziel García Cisneros (eloy.garcia@edu.uag.mx)

    usage: python rpc_server.py
"""

# Standard imports
from concurrent import futures
import time
import logging

# Third-party
import grpc

# Custom
import gato_pb2 as gato
import gato_pb2_grpc as rpc

logging.basicConfig(level="INFO")
LOGGER = logging.getLogger(__name__)

# Standard port for class assigments.
PORT = 20001


class GatoServer(
    rpc.GatoServerServicer
):  # inheriting here from the protobuf rpc file which is generated
    def __init__(self):
        # List with all the chat history
        self.moves = []

    # The stream which will be used to send new messages to clients
    def RecordMove(self, _, __):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages

        :param request_iterator:
        :param context:
        :return:
        """
        # For every client a infinite loop starts (in gRPC's own managed thread)
        last = 0
        while True:
            # Check if there are any new messages
            while len(self.moves) > last:
                move = self.moves[last]
                last += 1
                yield move

    def MakeMove(self, request: gato.Move, _):
        """
        This method is called when a clients sends a Note to the server.

        :param request:
        :param context:
        :return:
        """
        # this is only for the server console
        print(f"[{request.player}]-[{request.x},{request.y}]")
        # Add it to the chat history
        self.moves.append(request)
        return (
            gato.Empty()
        )  # something needs to be returned required by protobuf language, we just return empty msg


if __name__ == "__main__":
    """Control process workflow."""

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=5)
    )  # create a gRPC server
    rpc.add_GatoServerServicer_to_server(
        GatoServer(), server
    )  # register the server to gRPC

    LOGGER.info("Starting server. Listening...")
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()

    # Infinite loop to avoid main thread to finish
    while True:
        time.sleep(64 * 64 * 100)
