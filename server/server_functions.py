# server_functions.py

import socket
import os


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
            "user_added": 103,
            "disconnected": 104,
            "disconnect_fail": 105,
            "good_upload": 203,
            "bad_upload": 204,
            "file_exists": 205,
            "ok": 200
        }
        self.incoming_codes = {
            "auth": 100,
            "auth_new": 101,
            "exit": 102,
            "upload": 202,
            "override": 203,
            "no_override": 204,
            "sls": 301,
            "download": 302
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
    def incoming_client_communications(self, client_socket):
        while True:
            try:
                # Receive the client message
                message = client_socket.recv(1024).decode()
                
                # Break in case of corrupted message
                if not message:
                    break

                # Pass incoming message to message parser
                message_components = message.split()
                result =  self.parse_message_from_client(message = message_components, client_socket = client_socket)

                # Process internal code
                if result == self.outgoing_codes['good_auth']:
                    print(f"Total active connections: {self.active_connections}\n")
                elif result == self.outgoing_codes['bad_auth']: 
                    print("Connection closed.\n")
                    break
                elif result == self.outgoing_codes['disconnected']: 
                    print("\nUser disconnected.\n")
                    print(f"Active users: {self.active_connections}")
                    break
                elif result == self.outgoing_codes['good_upload']:
                    print("File successfully uploaded.\n")
                elif result == self.outgoing_codes['ok']:
                    print("Client requested fulfilled.\n")
                else:
                    break
            except Exception as error:
                print(f"Error encountered: {error}")
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
                    return self.outgoing_codes['good_auth']
                else:
                    print(f"{message[1]} already connected to network.\n")
                    
                    # Send bad auth code back to client and terminate connection
                    client_socket.send(str(self.outgoing_codes['dup_user']).encode())
                    client_socket.close()
                    return self.outgoing_codes['bad_auth']
            else:
                print(f"{message[1]} is not authorized.\n")

                # Send bad auth code back to client and terminate connection
                client_socket.send(str(self.outgoing_codes['bad_auth']).encode())
                client_socket.close()
                return self.outgoing_codes['bad_auth']
        
        # Client wants to register themselves with server
        elif message[0] == str(self.incoming_codes['auth_new']):
            print(f"Attempting to authorize new user: {message[1]}...\n")
            # Check if new users credentials exist already
            if message[1] in self.authenticated_users:
                print(f"{message[1]} is already an existing user.\n")
                # Tell client they provided invalid credentials
                client_socket.send(str(self.outgoing_codes['dup_user']).encode())
                client_socket.close()
                return self.outgoing_codes['bad_auth']
            else:
                print(f"{message[1]} is now an authorized user.\n")
                
                # Tell client they provided valid credentials and add them to the list of authorized users
                self.authenticated_users[message[1]] = message[2]
                client_socket.send(str(self.outgoing_codes['user_added']).encode())
                return self.outgoing_codes['good_auth']
            
        # Client wants to gracefully disconect from server
        elif message[0] == str(self.incoming_codes['exit']):
            print(f"Attempting to disconnect {message[1]}.")

            if message[1] in self.connected_users:
                self.connected_users.remove(message[1])
                self.active_connections -= 1

                client_socket.send(str(self.outgoing_codes['disconnected']).encode())
                client_socket.close()

                return self.outgoing_codes['disconnected']
            else:
                print(f"\nRequested to remove {message[1]}, but no such user is connected.\n")

                client_socket.send(self.outgoing_codes['disconnect_fail'].encode())
                return self.outgoing_codes['disconnect_fail']
        
        # Client wants to upload file to server database
        elif message[0] == str(self.incoming_codes['upload']):
            file_name = message[1]

            print(f'Receiving file `{file_name}` from client...\n')

            self.receive_file(file_name, client_socket)

            client_socket.send(str(self.outgoing_codes['good_upload']).encode())
            return self.outgoing_codes['good_upload']
    
        # Client wants to know files in servers cws
        elif message[0] == str(self.incoming_codes['sls']):
            print("Client requested files listed on server.\n")
    
            # Fetch current working directory
            cwd = os.getcwd()

            # Aggregate files in cwd
            local_files = os.listdir(cwd)
            file_names = ""

            # Define the allowed extensions
            allowed_extensions = ('.txt', '.mp3', '.wav', '.mp4', '.mkv', '.avi')

            # Add file to list if it has valid extension
            for entry in local_files:
                # Only add files with the allowed extensions
                if entry.endswith(allowed_extensions):
                    file_names += f"{entry}   "

            # Handle case when no files are on server
            if file_names == "":
                message = "No files in server's CWD."
                client_socket.send(message.encode())
            else:
                client_socket.send(file_names.encode())

            return self.outgoing_codes['ok']
        
        # Client wants to download a file off the server
        elif message[0] == str(self.incoming_codes['download']):
            print(f"Client has requested to download '{message[1]}'.\nSending...\n")

            # Open local file in read binary mode
            with open(message[1], "rb") as file:
                # Break file into binary chunks
                chunk = file.read(1024)

                while chunk:
                    client_socket.send(chunk)
                    chunk = file.read(1024)

            # Send EOF notification to server
            client_socket.send(b"<EOF>")
            return self.outgoing_codes['ok']

    # Desc: Receives a file from the client and writes it to the server's directory
    # Auth: Lang Towl
    # Date: 11/4/24
    def receive_file(self, file_name, client_socket):
        try:
            # Create an open a file in write binary mode
            file_path = os.path.join(os.getcwd(), file_name)

            #  Code to run if file alerady exists on server
            if os.path.exists(file_path):
                print("File already exists on server. Waiting for permission to override.\n")

                # Alert client to redundancy, wait for instructions
                client_socket.send(str(self.outgoing_codes['file_exists']).encode())
                response = client_socket.recv(1024).decode()

                if response == str(self.incoming_codes["override"]):
                    print("Permission to override granted.\n")
                else:
                    print("Permission to override denied.\n")
                    return
            else:
                client_socket.send(str(self.outgoing_codes['good_upload']).encode())    


            # Loop to copy contents of incoming chunks to file, open file in write binary mode
            with open(file_path, "wb") as file:
                print("Parsing file...\n")
                
                while True:
                    # Recieve data from client in chunks
                    data = client_socket.recv(1024)

                    # Escape sequence to run once end of file is reached
                    if b"<EOF>" in data:
                        file.write(data.replace(b"<EOF>", b""))
                        print(f"Finished recieving file '{file_name}'.\n")
                        break
                    
                    # Write data to open file
                    file.write(data)
        finally:
            file.close()