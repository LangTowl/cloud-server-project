# client_functions.py

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
            "auth": 100,
            "auth_new": 101
        }
        self.incoming_codes = {
            "good_auth": 100,
            "bad_auth": 101,
            "dup_user": 102
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
        user_to_authenticate = f"{self.outgoing_codes['auth']} {self.username} {self.password}"

        self.client_socket.send(user_to_authenticate.encode())

        # Wait for authentication response from server
        response = self.client_socket.recv(1024).decode()

        # Process server response
        if response == str(self.incoming_codes['good_auth']):
            self.authenticated = True
            print("\nAuthentication successful. You are now connected to the server.\n")
        elif response == str(self.incoming_codes['bad_auth']):
            print("\nAuthentication failed. Connection will be closed.\n")
            self.client_socket.close()
        elif response == str(self.incoming_codes['dup_user']):
            print("\nUser with same credentials already connected to network. Connection will be closed.\n")
            self.client_socket.close()

        return self.authenticated