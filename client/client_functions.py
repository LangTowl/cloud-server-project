# client_functions.py

import socket
import os
import time

METRIC = False

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
            "upload": 202,
            "override": 203,
            "no_override": 204,
            "sls": 301,
            "download": 302,
            "rm": 303
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
            "file_exists": 205,
            "file_DNE": 206,
            "ok": 200
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

        if commands[0] in self.outgoing_codes or commands[0] == "test":
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
            self.upload_file_subroutine(command_components[1])
        elif command_components[0] == "sls":
            self.sls_subroutine()
        elif command_components[0] == "download":
            self.dowload_file_subroutine(command_components[1])
        elif command_components[0] == "rm":
            self.delete_file_subroutine(command_components[1])
        elif command_components[0] == "test":
            self.set_METRIC_subroutine()
    
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

        # Define the allowed extensions
        allowed_extensions = ('.txt', '.mp3', '.wav', '.mp4', '.mkv', '.avi', '.jpg', '.jpeg', '.png')

        for entry in local_files:
            # Only add files with the allowed extensions
            if entry.endswith(allowed_extensions):
                file_names += f"{entry}   "
        
        print(f"\n{file_names}\n")

    # Desc: Upload file subroutine (metrics added by LK)
    # Auth: Lang Towl / Lukas Kelk
    # Date: 11/4/24 / 11/18/24
    def upload_file_subroutine(self, filename):
        
        #flag for marking the test
        global METRIC

        # Check to see if specific file is in cwd
        if not os.path.exists(filename):
            print("\nFile not found in the current working directory.\n")
            return
        else:
            print(f"\nPreparing to upload '{filename}'...")

            # Alert server to incoming file
            message = f"{self.outgoing_codes['upload']} {filename}"
            self.client_socket.send(message.encode())

            # Wait for status update of file upload
            response = self.client_socket.recv(1024).decode()

            # Prompt user to determine if they want to overive file
            if response == str(self.incoming_codes['file_exists']):
                override = input("\nFile exists on server, do you want to override this file? (y/n): ")

                # Escape function if they dont want to override
                if override.lower() == "n":
                    #TODO: SEND CODE BACK TO SERVER TELLING THEM NOT TO OVERRIDE
                    return
                else:
                    self.client_socket.send(str(self.outgoing_codes["override"]).encode())
                     
            if METRIC:
                #get size of file in bits
                fileSize = os.path.getsize(os.path.abspath(filename))
                #for performance metrics
                intialUploadtime = time.perf_counter()

            # Open local file in read binary mode
            with open(filename, "rb") as file:
                # Break file into binary chunks
                chunk = file.read(1024)

                while chunk:
                    self.client_socket.send(chunk)
                    chunk = file.read(1024)
            
            # Send EOF notification to server
            self.client_socket.send(b"<EOF>")

            if METRIC:
                #record finshed upload time
                finishedUploadTime = time.perf_counter()
                    
                #get duration
                duration = (finishedUploadTime - intialUploadtime)
                #in Mbps
                if duration > 0:
                    uploadSpeed = (fileSize * 8) / (duration * (10**6))
                else:
                    uploadSpeed = "Too Small"

            #get response from server
            response = self.client_socket.recv(1024).decode()

            # Notify user based on the result of upload
            if response == str(self.incoming_codes['good_upload']):
                print("\nFile uploaded to server successfully.\n")
                if METRIC:
                    print(f"Upload Speed:{uploadSpeed:.4f} Mbps\n")
            else:
                print("\nFile failed to upload to server.\n")

    # Desc: Request list of files from server
    # Auth: Lang Towl
    # Date: 11/4/24
    def sls_subroutine(self):
        # Request files in servers cwd
        message = f"{self.outgoing_codes['sls']}"
        self.client_socket.send(message.encode())

        # Wait for server to fulfil request
        response = self.client_socket.recv(1024).decode()
        print(f"\n{response}\n")

    # Desc: Request list of files from server
    # Auth: Lang Towl
    # Date: 11/4/24
    def dowload_file_subroutine(self, file_name):
        # Check to see if file exists on server
        message = f"{self.outgoing_codes['sls']}"
        self.client_socket.send(message.encode())

        # Wait for server to fulfil request
        response = self.client_socket.recv(1024).decode()

        # If file exists on server
        if file_name in response:
            try:
                # Make new file in clients CWD
                file_path = os.path.join(os.getcwd(), file_name)

                # Request download initiation
                request_dowload = f"{self.outgoing_codes['download']} {file_name}"
                self.client_socket.send(request_dowload.encode())

                # Loop to copy contents of incoming chunks to file, open file in write binary mode
                with open(file_path, "wb") as file:
                    print("\nDownloading file...\n")
                    
                    while True:
                        # Recieve data from client in chunks
                        data = self.client_socket.recv(1024)

                        # Escape sequence to run once end of file is reached
                        if b"<EOF>" in data:
                            file.write(data.replace(b"<EOF>", b""))
                            print(f"Finished recieving file '{file_name}'.\n")
                            break
                        
                        # Write data to open file
                        file.write(data)
            finally:
                file.close()

        # If file doesn't exists on server
        else:
            print("\nFile does not exist on server.\n")
    
    # Desc: Delete file from server
    # Auth: Lukas Kelk
    # Date: 11/16/24
    def delete_file_subroutine(self, file_name):
        
        print(f"\nRequesting to delete '{file_name}' from the server...\n")

        #send message code rm
        message = f"{self.outgoing_codes['rm']} {file_name}"
        self.client_socket.send(message.encode())

        #wait for response from the server
        response = self.client_socket.recv(1024).decode()

        #handlinlg the response from the server
        if response == str(self.incoming_codes['ok']):
            print(f"The file '{file_name}' has been successfully deleted from the server.\n")
        elif response == str(self.incoming_codes['file_DNE']):
            print(f"Failed to delete the file '{file_name}' from the server. This File might not exist.\n")
   
    # Desc: set metrics to true or falsesubroutine
    # Auth: Lukas Kelk
    # Date: 11/16/24
    def set_METRIC_subroutine(self):
        global METRIC
        
        if(METRIC):
            METRIC = False
            print("\nThe Client will no longer give performance metrics\n")
        else:
            METRIC = True
            print("\nThe Client will now give performance metrics\n")