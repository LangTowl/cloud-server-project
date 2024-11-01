# server_functions.py

import socket
import threading
import sys

# Desc: Client object
# Auth: Lang Towl
# Date: 10/31/24
class Server:
    # Desc: Server object initializer
    # Auth: Lang Towl
    # Date: 11/1/24
    def __init__(self, ip = '127.0.0.1', port = 3300):
        self.ip = ip
        self.port = port
        self.server_socket = None
        self.active_connections = 0
        self.authenticated_users = {
            "Lang": "123"
        }
        self.outgoing_codes = {
            "good_auth": 100,
            "bad_auth": 101
        }
        self.incoming_codes = {
            "auth": 100,
            "auth_new": 101
        }
    
    # Desc: Initiate client socket
    # Auth: Lang Towl
    # Date: 11/1/24
    def init_server(self):
        # Create a socket object, bidning it to the port and IP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))

        # Begin listening for incomming connections
        self.server_socket.listen()
        print("Server is listening...")

    
    # Desc: handle new client connections
    # Auth: Lang Towl
    # Date: 10/31/24
    def new_client_connection(self, client_socket):
        # Increase the number of active connections
        self.active_connections += 1
        print(f"Total active connections: {self.active_connections}\n")

        while True:
            # Receive the client message
            message = client_socket.recv(1024).decode()
            message_components = message.split()
                
            # Break in case of corrupted message
            if not message:
                break

            # Pass incoming message to message parser
            self.parse_message_from_client(message = message_components)

    # Desc: Function parses input from client thread
    # Auth: Lang Towl
    # Date: 10/31/24
    def parse_message_from_client(self, message):
        # Switch statement to determine subroutine to run
        if message[0] == '100':
            print(f"Attempting to authenticate {message[1]}...\n")

            if message[1] in self.authenticated_users and self.authenticated_users[message[1]] == message[2] :
                print(f"{message[1]} authorized.\n")
            else:
                print(f"{message[1]} is not authorized.\n")

