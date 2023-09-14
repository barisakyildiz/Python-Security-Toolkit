import sys
import socket
import getopt
import threading
import subprocess


#global var
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def usage():
    print ("Not NetCat Tool")
    print()
    print ("Usage: notNCAT.py -t target_host -p port")
    print ("-l --listen - listen on [host]:[port] for incoming connections")
    print ("-e --execute=file_to_run - execute the given file upon receiving a connection")
    print ("-c --command - initialize a command shell")
    print ("-u --upload=destination - upon receiving connection upload a file and write to [destination]")
    print
    print
    print ("Examples: ")
    print ("notNCAT.py -t 192.168.0.1 -p 5555 -l -c")
    print ("notNCAT.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print ("notNCAT.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print ("echo 'ABCDEFGHI' | ./notNCAT.py -t 192.168.11.12 -p 135")
    sys.exit(0)

def clientSender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))
    
        if len(buffer):
            client.send(buffer.encode())
        while True:
            #wait for data block
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode()

                if recv_len < 4096:
                    break
            print(response)
        
            #waiting for more input
            buffer = input("")
            buffer += "\n"
            buffer = buffer.encode()

            #send it off
            client.send(buffer)
    except Exception as e:
        print("[*] Exception Occured: {} \nExiting.".format(e))
        client.close()

def serverLoop():
    global target

    #if no target is given, we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        #thread to handle the new client
        client_thread = threading.Thread(target=clientHandler, args=(client_socket,))
        client_thread.start()

def runCommand(command):
    #trim the newline
    command = command.rstrip()

    #run the command and get the output back
    try:
        output = (subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)).decode()
    except:
        output = "Failed to execute command.\r\n"
    return output

def clientHandler(client_socket):
    global upload
    global execute
    global command

    #check for upload
    if len(upload_destination):
        #read in all of the bytes and write to our destination
        file_buffer = ""

        #keep reading data until none is available

        while True:
            data = client_socket.recv(1024).decode()

            if not data:
                break
            else:
                file_buffer += data

        # now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            
            #ack that we wrote the file out 
            client_socket.send(("Successfully saved file to {}\r\n".format(upload_destination)).encode())
        except Exception as e:
            client_socket.send(("Failed to save file to {}\r\n".format(upload_destination)).encode())

    #check for command execution
    if len(execute):
        #run the command
        output = runCommand(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send("<notNCAT:#> ".encode())

            #now we recieve until we see a linefeed
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += (client_socket.recv(1024)).decode()

            response = runCommand(cmd_buffer)

            #send back the response
            client_socket.send(response.encode())  

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    #read the options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu", ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as e:
        print(str(e))
        usage()
    
    for o, a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"

    # Are we going to listen or just send data from stdin?
    if not listen and len(target) and port > 0:

        #read in the buffer from the commandline
        #this will block it, so press CTRL-D if not sending input
        #to stdin
        buffer = sys.stdin.read()

        # send data off
        clientSender(buffer)

    if listen:
        serverLoop()

main()