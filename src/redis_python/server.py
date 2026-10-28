"""Serve the command handler to Redis clients over TCP."""

import socket
import threading

from .commands import CommandHandler
from .protocols.parser import RESPParser
from .protocols.values import RESP, Array, BulkString, SimpleError
from .store import Store

HOST = "localhost"
PORT = 1234


def is_command(value: RESP) -> bool:
    """Return whether a value is a non-empty array of bulk strings."""
    return (
        isinstance(value, Array)
        and bool(value.data)
        and all(isinstance(item, BulkString) and item.data is not None for item in value.data)
    )


def handle_client(
    client: socket.socket, handler: CommandHandler, lock: threading.Lock
) -> None:
    """Answer commands from one client until it disconnects."""
    buffer = b""
    with client:
        while True:
            chunk = client.recv(4096)
            if not chunk:
                return
            buffer += chunk

            parser = RESPParser(buffer)
            while True:
                try:
                    command = parser.parse()
                except EOFError:
                    break
                except ValueError:
                    client.sendall(SimpleError("ERR Protocol error").encode())
                    return

                if not is_command(command):
                    reply: RESP = SimpleError("ERR commands must be arrays of bulk strings")
                else:
                    with lock:
                        reply = handler.handle(command)
                client.sendall(reply.encode())

            buffer = buffer[parser.cursor :]


def main() -> None:
    handler = CommandHandler(Store())
    lock = threading.Lock()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[+] Redis clone server listening on {HOST}:{PORT}")

        try:
            while True:
                client, addr = server.accept()
                print(f"[+] Accepted connection from {addr[0]}:{addr[1]}")
                threading.Thread(
                    target=handle_client, args=(client, handler, lock), daemon=True
                ).start()
        except KeyboardInterrupt:
            print("\n[+] Shutting down")


if __name__ == "__main__":
    main()
