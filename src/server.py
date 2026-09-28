import socket
import threading

hostname: str = "localhost"
port:int = 1234

server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((hostname, port))
server.listen(5)

print(f"[+] Listening on port {hostname}: {port}")

def handler_client(client: socket.socket) -> None:
    request = client.recv(1024)
    print(f"[+] Received: {request}")
    client.send("Ping received".encode())
    client.close()

while True:
    client, addr = server.accept()
    print(f"[+] Accepted connection from: {addr[0]}: {addr[1]}")

    handler = threading.Thread(target=handler_client, args=(client,))
    handler.start()
