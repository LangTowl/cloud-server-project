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
    def __init__(self, ip = '0.0.0.0', port = 8080):
        self.ip = ip
        self.port = port
        self.server_socket = None
        self.active_connections = 0
        self.connected_users = []
        self.authenticated_users = { }
        self.outgoing_codes = {
            "good_auth": 100,
            "bad_auth": 101,
            "dup_user": 102,
            "user_added": 103
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
        while True:
            try:
                # Receive the client message
                message = client_socket.recv(1024).decode()
                
                # Break in case of corrupted message
                if not message:
                    break

                # Pass incoming message to message parser
                message_components = message.split()
                keep_connection =  self.parse_message_from_client(message = message_components, client_socket = client_socket)

                # Terminate connection if bad auth
                if keep_connection:
                    print(f"Total active connections: {self.active_connections}\n")
                else: 
                    print("Connection closed due to failed authentication.\n")
                    break
            except:
                print("Error: Issue encountered when terminating client connection.")
                break
    
    # Desc: Function checks list of current connected users to prevent duplicate connections
    # Auth: Lang Towl
    # Date: 11/2/24
    def user_already_online(self, user) -> bool:
        if user in self.connected_users:
            return True
        else:
            return False

    # Desc: Function parses input from client thread
    # Auth: Lang Towl
    # Date: 10/31/24
    def parse_message_from_client(self, message, client_socket):
        # Switch statement to determine subroutine to run

        # Client wishing to connect, is attempting to authorize
        if message[0] == str(self.incoming_codes['auth']):
            print(f"Attempting to authenticate {message[1]}...\n")

            if message[1] in self.authenticated_users and self.authenticated_users[message[1]] == message[2]:
                if self.user_already_online(message[1]) == False:
                    print(f"{message[1]} authorized.\n")

                    # Increase the number of active connections
                    self.active_connections += 1

                    # Send good auth code back to client
                    client_socket.send(str(self.outgoing_codes['good_auth']).encode())
                    self.connected_users.append(message[1])
                    return True
                else:
                    print(f"{message[1]} already connected to network.\n")
                    
                    # Send bad auth code back to client and terminate connection
                    client_socket.send(str(self.outgoing_codes['dup_user']).encode())
                    client_socket.close()
                    return False
            else:
                print(f"{message[1]} is not authorized.\n")

                # Send bad auth code back to client and terminate connection
                client_socket.send(str(self.outgoing_codes['bad_auth']).encode())
                client_socket.close()
                return False
        
        # Client wants to register themselves with server
        elif message[0] == str(self.incoming_codes['auth_new']):
            print(f"Attempting to authorize new user: {message[1]}...\n")
            # Check if new users credentials exist already
            if message[1] in self.authenticated_users:
                print(f"{message[1]} is already an existing user.\n")
                # Tell client they provided invalid credentials
                client_socket.send(str(self.outgoing_codes['dup_user']).encode())
                client_socket.close()
                return False
            else:
                print(f"{message[1]} is now an authorized user.\n")
                
                # Tell client they provided valid credentials and add them to the list of authorized users
                self.authenticated_users[message[1]] = message[2]
                client_socket.send(str(self.outgoing_codes['user_added']).encode())
                return True