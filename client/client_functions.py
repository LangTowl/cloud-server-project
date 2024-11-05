# client_functions.py

import socket
import os

# Desc: Client object
# Auth: Lang Towl
# Date: 10/31/24
class Client:
    # Desc: Client object initializer
    # Auth: Lang Towl
    # Date: 11/1/24
    def __init__(self, ip = '127.0.0.1', port = 8080, username = None, password = None):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.authenticated = False
        self.key = None
        self.client_socket = None
        self.outgoing_codes = {
            "auth": 100,
            "auth_new": 101,
            "exit": 102,
            "ls": 201,
            "upload": 202
        }
        self.incoming_codes = {
            "good_auth": 100,
            "bad_auth": 101,
            "dup_user": 102,
            "user_added": 103,
            "disconnected": 104,
            "disconnect_fail": 105,
            "good_upload": 203,
            "bad_upload": 204,
            "file_exists": 205
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
            print("User with same credentials is already connected to network. Connection will be closed.\n")
            self.client_socket.close()

        return self.authenticated

    # Desc: Contacts server to authenticate client
    # Auth: Lang Towl
    # Date: 11/1/24
    def athorize_new_client(self):
        user_to_authorize = f"{self.outgoing_codes['auth_new']} {self.username} {self.password}"

        self.client_socket.send(user_to_authorize.encode())

        response = self.client_socket.recv(1024).decode()

        # Process server response
        if response == str(self.incoming_codes['user_added']):
            print("\nRequest received by server. Waiting for server to vailidate new client...")
        elif response == str(self.incoming_codes['dup_user']):
            print("\nA user with these credentials already exists.\n")

    # Desc: Check validity of instruction
    # Auth: Lang Towl
    # Date: 11/4/24
    def validate_command(self, command):
        commands = command.split()

        if commands[0] in self.outgoing_codes:
            return True
        else:
            return False

    # Desc: Outgoing command handler
    # Auth: Lang Towl
    # Date: 11/4/24
    def direct_outgoing_commands(self, command):
        command_components = command.split()

        if command_components[0] == "exit":
            self.exit_subroutine()
        elif command_components[0] == "ls":
            self.ls_subroutine()
        elif command_components[0] == "upload":
            self.upload_file(command_components[1])
    
    # Desc: Exit subroutine
    # Auth: Lang Towl
    # Date: 11/4/24
    def exit_subroutine(self):
        message = f"{self.outgoing_codes['exit']} {self.username}"

        self.client_socket.send(message.encode())
        response = self.client_socket.recv(1024).decode()

        if response == str(self.incoming_codes['disconnected']):
            self.authenticated = False
        else:
            self.incoming_codes['disconnect_fail']
    
    # Desc: Show files in CWD subroutine
    # Auth: Lang Towl
    # Date: 11/4/24
    def ls_subroutine(self):
        # Fetch current working directory
        cwd = os.getcwd()

        # Aggregate files in cwd
        local_files = os.listdir(cwd)
        file_names = ""

        for entry in local_files:
            file_names += f"{entry}   "
        
        print(f"\n{file_names}\n")

    # Desc: Upload file subroutine
    # Auth: Lang Towl
    # Date: 11/4/24
    def upload_file(self, filename):
        # Check to see if specific file is in cwd
        if not os.path.exists(filename):
            print("\nFile not found in the current working directory.\n")
            return
        else:
            print(f"\nPreparing to upload '{filename}...\n")

            message = f"{self.outgoing_codes['upload']} {filename}"
            self.client_socket.send(message.encode())
            
            with open(filename, "rb") as file:
                # Break file into binary chunks
                chunk = file.read(1024)

                while chunk:
                    self.client_socket.send(chunk)
                    chunk = file.read(1024)

            # Send EOF notification to server
            self.client_socket.send(b"<EOF>")

            response = self.client_socket.recv(1024).decode()
            print(str(response))