import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print("[*] Listening on {}:{}".format(bind_ip, bind_port))

#client-handling thread
def handlingClient(client_socket):
    request = client_socket.recv(1024)
    print("[*] Recieved: {}".format(request.decode()))

    #send back a response
    client_socket.send("ACKNOWLEDGE".encode())
    client_socket.close()

while True:
    client, addr = server.accept()
    print("[*] Incoming Connection From: {}:{}".format(addr[0], addr[1]))

    #client thread
    client_handler = threading.Thread(target=handlingClient, args=(client,))
    client_handler.start()