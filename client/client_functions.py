import socket
import threading
import sys

# Desc: Client object
# Auth: Lang Towl
# Date: 10/31/24
class Client:
    # Desc: Client object initializer
    # Auth: Lang Towl
    # Date: 11/1/24
    def __init__(self, ip = '127.0.0.1', port = 3300, username = None, password = None):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.authenticated = False
        self.key = None
        self.client_socket = None
        self.outgoing_codes = {
            "authenticate": 1
        }
        self.incoming_codes = {
            "good_auth": 1,
            "bad_auth": 2
        }

    # Desc: Initiate client socket
    # Auth: Lang Towl
    # Date: 11/1/24
    def init_client(self, username, password):
        # Update client object
        self.username = username
        self.password = password

        # Create a socket object, connecting it to the port and IP
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.ip, self.port))

    # Desc: Contacts server to authenticate client, returns status of client authetnication
    # Auth: Lang Towl
    # Date: 11/1/24
    def authenticate_client(self) -> bool:
        message = "test"

        self.client_socket.send(message.encode())
        self.client_socket.close()

        return self.authenticated

    

# Desc: Helper function to handle printing without disrupting the input prompt
# Auth: Lang Towl
# Date: 10/31/24
def print_with_prompt(message):
    # Clear the current line (80 characters)
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    print(message) 

    # Redisplay the prompt
    sys.stdout.write("You: ")                       
    sys.stdout.flush()

# Desc: Handle stream inbound messages to client
# Auth: Lang Towl
# Date: 10/31/24
def client_receive(client_socket):
    # Continually checks for inbound messages to client
    while True:
        try:
            # Decode inbound response from bytes into string
            response = client_socket.recv(1024).decode()
            if response:
                print_with_prompt(f"Server: {response}")
            else:
                break
        except:
            break

# Desc: Send outputbound messages from client
# Auth: Lang Towl
# Date: 10/31/24
def client_send(client_socket):
    while True:
        # Get client input, message to be sent
        message = input("You: ")

        # Check for escape case
        if message.lower() == 'exit':
            break
        
        # Sends byte-encoded message
        client_socket.send(message.encode())

    # Closses socket in event of escape case
    client_socket.close()
    print("Connection closed by client.\n")

# Desc: Initiate client socket
# Auth: Lang Towl
# Date: 10/31/24
def init_client(ip, port):
    # Create a socket object, connecting it to the port and IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))

    print(f'Connected to server {ip} on port {port}.\n')

    # Create threads for sending and receiving messages
    threading.Thread(target=client_receive, args=(client_socket,)).start()
    threading.Thread(target=client_send, args=(client_socket,)).start()
    
    