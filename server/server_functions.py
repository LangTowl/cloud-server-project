# server_functions.py

import socket
import os
import time
import shutil

# Desc: Client object
# Auth: Lang Towl
# Date: 10/31/24
class Server:
    # Desc: Server object initializer
    # Auth: Lang Towl
    # Date: 11/1/24
    def __init__(self, ip = '10.128.0.3', port = 8080):
        self.ip = ip
        self.port = port
        self.home = os.getcwd()
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
            "file_DNE": 206,
            "dir_AE": 207,
            "dir_DNE": 208,
            "dir_top": 209,
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
            "download": 302,
            "rm": 303,
            "mkdir": 304,
            "rmdir": 305,
            "cd": 306
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
                elif result == self.outgoing_codes['bad_upload']:
                    print("File uploaded process terminated.\n")
                elif result == self.outgoing_codes['ok']:
                    print("Client requested fulfilled.\n")
                elif result == self.outgoing_codes['file_DNE']:
                    print("There is no file with that path.\n")
                elif result == self.outgoing_codes['dir_AE']:
                    print("This directory already exists.\n")
                elif result == self.outgoing_codes['dir_DNE']:
                    print("That directory does not exist\n")
                elif result == self.outgoing_codes['dir_top']:
                    print("You are unable to move up a directory")
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
        
        # Client wishing to connect, is attempting to authorize
        if message[0] == str(self.incoming_codes['auth']):
            print(f"Attempting to authenticate {message[1]}...\n")

            return self.authenticate_user_subroutine(message = message, client_socket = client_socket)
        
        # Client wants to register themselves with server
        elif message[0] == str(self.incoming_codes['auth_new']):
            print(f"Attempting to authorize new user: {message[1]}...\n")

            return self.register_user_subroutine(message = message, client_socket = client_socket)
            
        # Client wants to gracefully disconect from server
        elif message[0] == str(self.incoming_codes['exit']):
            print(f"Attempting to disconnect {message[1]}.")

            return self.exit_subroutine(message = message, client_socket = client_socket)
        
        # Client wants to upload file to server database
        elif message[0] == str(self.incoming_codes['upload']):
            print(f'Receiving file `{message[1]}` from client...\n')

            return self.receive_file_subroutine(message[1], client_socket)
    
        # Client wants to know files in servers cws
        elif message[0] == str(self.incoming_codes['sls']):
            print("Client requested files listed on server.\n")
    
            return self.sls_subroutine(message = message, client_socket = client_socket)
        
        # Client wants to download a file off the server
        elif message[0] == str(self.incoming_codes['download']):
            print(f"Client has requested to download '{message[1]}'.\n\nSending...\n")

            return self.download_subroutine(message = message, client_socket = client_socket)
        
        elif message[0] == str(self.incoming_codes['rm']):
            print(f"Client has requested to delete '{message[1]}'.\n")

            return self.delete_subroutine(message = message, client_socket = client_socket)
        
        elif message[0] == str(self.incoming_codes['mkdir']):
            print(f"Client has requested to create a new directory with the file path '{message[1]}'.\n")

            return self.make_directory_subroutine(message = message, client_socket=client_socket)
        
        elif message[0] == str(self.incoming_codes['rmdir']):
            print(f"Client has requested to delete a directory with the file path '{message[1]}'.\n")

            return self.delete_directory_subroutine(message = message, client_socket=client_socket)

        elif message[0] == str(self.incoming_codes['cd']):
            print(f"Client has requested to change the filepath to '{message[1]}'.\n")

            return self.change_directory_subroutine(message = message, client_socket=client_socket)


    # Desc: Authetnicate user subroutine
    # Auth: Lang Towl
    # Date: 11/11/24
    def authenticate_user_subroutine(self, message, client_socket):
        if message[1] in self.authenticated_users and self.authenticated_users[message[1]] == message[2]:
            if self.user_already_online(message[1]) == False:
                print(f"{message[1]} authorized.\n")

                # Increase the number of active connections
                self.active_connections += 1

                # Send good auth code back to client
                response = f"{self.outgoing_codes['good_auth']} {self.home}"
                client_socket.send(str(response).encode())
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



    # Desc: Register new authorized user
    # Auth: Lang Towl
    # Date: 11/11/24
    def register_user_subroutine(self, message, client_socket):
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
            message = str(os.getcwd())
            client_socket.send(message.encode())
            return self.outgoing_codes['good_auth']
        

    # Desc: Disconnect client from server
    # Auth: Lang Towl
    # Date: 11/11/24
    def exit_subroutine(self, message, client_socket):
        # Check to see if requested user is currently logged in
        if message[1] in self.connected_users:
            # Remove user from connected user list, decrememnt active user count
            self.connected_users.remove(message[1])
            self.active_connections -= 1

            # Update client and status of removal
            client_socket.send(str(self.outgoing_codes['disconnected']).encode())
            client_socket.close()

            return self.outgoing_codes['disconnected']
        else:
            print(f"\nRequested to remove {message[1]}, but no such user is connected.\n")

            client_socket.send(self.outgoing_codes['disconnect_fail'].encode())
            return self.outgoing_codes['disconnect_fail']



    # Desc: sls subroutine
    # Auth: Lang Towl
    # Date: 11/11/24
    def sls_subroutine(self, message, client_socket):
        # Fetch current working directory
        cwd = os.getcwd()

        # Aggregate files in cwd
        local_files = os.listdir(cwd)
        file_names = ""

        # Define the allowed extensions
        allowed_extensions = ('.txt', '.mp3', '.wav', '.mp4', '.mkv', '.avi', '.jpg', '.jpeg', '.png')

        # Add file to list if it has valid extension
        for entry in local_files:
            # Only add files with the allowed extensions
            if entry.endswith(allowed_extensions) or (os.path.isdir(entry) and entry != "__pycache__"):
                file_names += f"{entry}   "

        # Handle case when no files are on server
        if file_names == "":
            message = "No files in server's CWD."
            client_socket.send(message.encode())
        else:
            client_socket.send(file_names.encode())

        return self.outgoing_codes['ok']
    


    # Desc: Receives a file from the client and writes it to the server's directory
    # Auth: Lang Towl
    # Date: 11/4/24
    def receive_file_subroutine(self, file_name, client_socket):
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
                elif response == str(self.incoming_codes["no_override"]):
                    print("Permission to override denied.\n")
                    # client_socket.send(str(self.outgoing_codes['bad_upload']).encode()) 
                    return self.outgoing_codes['bad_upload']
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
            
            client_socket.send(str(self.outgoing_codes['good_upload']).encode())
            return self.outgoing_codes['good_upload']
        finally:
            if 'file' in locals(): 
                file.close()
    


    # Desc: Download a file from server to client
    # Auth: Lang Towl
    # Date: 11/11/24
    def download_subroutine(self, message, client_socket):
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


    # Desc: Delete a File on Server side from client request
    # Auth: Lukas kelk
    # Date: 11/16/24
    def delete_subroutine(self, message, client_socket):

        path = os.path.join(os.getcwd(), message[1])

        if os.path.exists(path):
            #if the file path exists remove, 
            os.remove(path)
            print(f"File '{message[1]}' has been deleted successfully.\n")
            client_socket.send(str(self.outgoing_codes['ok']).encode())
            return self.outgoing_codes['ok']
        else:
            # File does not exist
            print(f"\nFile '{message[1]}' does not exist on server.\n")
            client_socket.send(str(self.outgoing_codes['file_DNE']).encode())
            return self.outgoing_codes['file_DNE']
    
    # Desc: Make new directory in server
    # Auth: Spencer T. Robinson
    # Date: 11/21/24
    def make_directory_subroutine(self, message, client_socket):
        print("Entered make_directory_subroutine\n")
        print(os.getcwd())
        path = message[1]
        if os.path.exists(path):
            #if the file path exists, send back 
            print(f"Directory '{path}' already exists\n")
            client_socket.send(str(self.outgoing_codes['dir_AE']).encode())
            return self.outgoing_codes['dir_AE']
        else:
            #directory dne, make one
            print(f"Creating directory named '{path}'\n")
            os.mkdir(path)
            client_socket.send(str(self.outgoing_codes['ok']).encode())
            return self.outgoing_codes['ok']
        
    # Desc: Delete a directory in server
    # Auth: Spencer T. Robinson
    # Date: 11/21/24
    def delete_directory_subroutine(self, message, client_socket):
        print("Entered delete_directory_subroutine\n")
        path = message[1]
        if os.path.exists(path):
            #if the file path exists, send back 
            print(f"Deleting '{path}' directory\n")
            shutil.rmtree(path)
            client_socket.send(str(self.outgoing_codes['ok']).encode())
            return self.outgoing_codes['ok']
        else:
            #directory dne, return
            print(f"Directory '{path}' does not exist\n")
            client_socket.send(str(self.outgoing_codes['dir_DNE']).encode())
            return self.outgoing_codes['dir_DNE']

    def change_directory_subroutine(self, message, client_socket):
        print("Entered change_directory_subroutine\n")

        #slightly hardcoded file path req, in order to limit cd ..
        if(len(message[1]) < len(self.home)): 
            print(f"Unable to move up directory\n")
            client_socket.send(str(self.outgoing_codes['dir_top']).encode())
            return self.outgoing_codes['dir_top']
        elif(message[1] == ".."):
            path = os.path.dirname(os.getcwd())
        else:
            path = message[1]
        
        if os.path.exists(path):
            #if the file path exists, send back 
            print(f"Change directory to '{path}'\n")
            os.chdir(path)
            client_socket.send(str(self.outgoing_codes['ok']).encode())
            return self.outgoing_codes['ok']
        else:
            #directory dne, return
            print(f"Directory '{path}' does not exist\n")
            client_socket.send(str(self.outgoing_codes['dir_DNE']).encode())
            return self.outgoing_codes['dir_DNE']