import socket

target_host: str = "localhost"
target_port: int = 1234

client: socket.socket = socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))


client.send("GET / HTTP/1.1\r\nHost: redis-clone.com\r\n\r\n".encode())
response = client.recv(1024)

print(response.decode())
