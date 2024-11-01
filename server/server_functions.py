import socket
import threading
import sys

# Desc: Helper function to handle printing without disrupting the input prompt
# Auth: Lang Towl
# Date: 10/31/24
def print_with_prompt(message):
    # Clear the current line (80 characters)
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    print(message) 
    
    # Redisplay the prompt
    sys.stdout.write("Server: ")                       
    sys.stdout.flush()

# Desc: Handle stream inbound messages to server
# Auth: Lang Towl
# Date: 10/31/24
def server_receive(server_socket):
    # Continually checks for inbound messages to client
    while True:
        try:
             # Decode inbound response from bytes into string
            response = server_socket.recv(1024).decode()
            if response:
                print_with_prompt(f"Client: {response}")
            else:
                break
        except:
            break

# Desc: Send outputbound messages from server
# Auth: Lang Towl
# Date: 10/31/24
def server_send(server_socket):
    while True:
        # Get server input, message to be sent
        message = input("Server: ")

        # Check for escape case
        if message.lower() == 'exit':
            break
        
        # Sends byte-encoded message
        server_socket.send(message.encode())

    # Closses socket in event of escape case
    server_socket.close()
    print("Connection closed by server.\n")

def init_server(ip, port):
    # Create a socket object, bidning it to the port and IP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((ip, port))

    # Begin listening for incomming connections
    server_socket.listen(1)
    print("Server is listening...\n")

    # Accept inbound communication
    connection, address = server_socket.accept()
    print(f'Connected to {address}')

    # Create threads for sending and receiving messages
    threading.Thread(target=server_receive, args=(connection,)).start()
    threading.Thread(target=server_send, args=(connection,)).start()