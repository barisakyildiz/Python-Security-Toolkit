import socket

target_host = "127.0.0.1"
target_port = 9999

#create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect to client
client.connect((target_host, target_port))

#send some data
client.send("abcdef \r\n\r\n".encode())

#recieve some data
response = client.recv(4096)

print(response.decode())