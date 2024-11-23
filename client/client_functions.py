# client_functions.py

import socket
import os
import time
import analysis as analysis
METRIC = False

# Desc: Client object
# Auth: Lang Towl
# Date: 10/31/24
class Client:
    # Desc: Client object initializer
    # Auth: Lang Towl
    # Date: 11/1/24
    def __init__(self, ip = '127.0.0.1', port = 8080, username = None, password = None, timeout = 10):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.s_cwd = ""
        self.s_cwd_constant = ""
        self.authenticated = False
        self.key = None
        self.client_socket = None
        self.timeout = timeout
        self.outgoing_codes = {
            "auth": 100,
            "auth_new": 101,
            "exit": 102,
            "ls": 201,
            "upload": 202,
            "override": 203,
            "no_override": 204,
            "s_pwd": 205,
            "sls": 301,
            "download": 302,
            "rm": 303,
            "mkdir": 304,
            "rmdir": 305,
            "cd": 306

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
            "dir_AE": 207,
            "dir_DNE": 208,
            "dir_top": 209,
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
        self.client_socket.settimeout(self.timeout)
        self.client_socket.connect((self.ip, self.port))

    # Desc: Contacts server to authenticate client, returns status of client authetnication
    # Auth: Lang Towl
    # Date: 11/1/24
    def authenticate_client(self) -> bool:
        user_to_authenticate = f"{self.outgoing_codes['auth']} {self.username} {self.password}"

        self.client_socket.send(user_to_authenticate.encode())

        # Wait for authentication response from server
        response = self.safe_recv(1024)
        components = response.split()

        # Process server response
        if components[0] == str(self.incoming_codes['good_auth']):
            self.authenticated = True
            print("\nAuthentication successful. You are now connected to the server.\n")
        elif components[0] == str(self.incoming_codes['bad_auth']):
            print("\nAuthentication failed. Connection will be closed.\n")
            self.client_socket.close()
        elif components[0] == str(self.incoming_codes['dup_user']):
            print("User with same credentials is already connected to network. Connection will be closed.\n")
            self.client_socket.close()

        # If good auth, update server current working directory
        if len(components) > 1:
            self.s_cwd = components[1]
            self.s_cwd_constant = components[1]

        return self.authenticated

    # Desc: Contacts server to authenticate client
    # Auth: Lang Towl
    # Date: 11/1/24
    def athorize_new_client(self):
        user_to_authorize = f"{self.outgoing_codes['auth_new']} {self.username} {self.password}"

        self.client_socket.send(user_to_authorize.encode())

        response = self.safe_recv(1024)

        # Process server response
        if response == str(self.incoming_codes['user_added']):
            print("\nRequest received by server. Waiting for server to vailidate new client...")
        elif response == str(self.incoming_codes['dup_user']):
            print("\nA user with these credentials already exists.\n")

        response = self.safe_recv(1024)
        self.s_cwd = response
        self.s_cwd_constant = response



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
            global METRIC
            METRIC = analysis.set_METRIC(METRIC)
        elif command_components[0] == "mkdir":
            self.make_directory_subroutine(command_components[1])
        elif command_components[0] == "rmdir":
            self.delete_directory_subroutine(command_components[1])
        elif command_components[0] == "cd":
            self.change_directory_subroutine(command_components[1])
        elif command_components[0] == "s_pwd":
            self.server_pwd()    

    # Desc: Exit subroutine
    # Auth: Lang Towl
    # Date: 11/4/24
    def exit_subroutine(self):
        message = f"{self.outgoing_codes['exit']} {self.username}"

        self.safe_send(message)
        response = self.safe_recv(1024)

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

            if METRIC:
                sendRequest = time.perf_counter()

            self.safe_send(message)

            # Wait for status update of file upload
            response = self.safe_recv(1024)

            if METRIC:
                gotRequest = time.perf_counter()

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
       

            #get response from server
            response = self.safe_recv(1024)

            # Notify user based on the result of upload
            if response == str(self.incoming_codes['good_upload']):
                print("\nFile uploaded to server successfully.\n") 
                if METRIC:
                    analysis.log_upload_metircs(sendRequest,gotRequest,finishedUploadTime,intialUploadtime,os.path.abspath(filename))  
            else:
                print("\nFile failed to upload to server.\n")

    # Desc: Request list of files from server
    # Auth: Lang Towl
    # Date: 11/4/24
    def sls_subroutine(self):
        # Request files in servers cwd
        message = f"{self.outgoing_codes['sls']}"
        self.safe_send(message)

        # Wait for server to fulfil request
        response = self.safe_recv(1024)
        print(f"\n{response}\n")

    # Desc: Request list of files from server / metrics
    # Auth: Lang Towl / Lukas Kelk
    # Date: 11/4/24 / 11/20/24
    def dowload_file_subroutine(self, file_name):
        # Check to see if file exists on server
        message = f"{self.outgoing_codes['sls']}"
        self.safe_send(message)

        # Wait for server to fulfil request
        response = self.safe_recv(1024)

        # If file exists on server
        if file_name in response:
            try:
                # Make new file in clients CWD
                file_path = os.path.join(os.getcwd(), file_name)

                # Request download initiation
                request_dowload = f"{self.outgoing_codes['download']} {file_name}"
                if METRIC:
                    sendRequest = time.perf_counter()
                self.client_socket.send(request_dowload.encode())

                if(METRIC):
                    #for performance metrics
                    intialDownloadtime = time.perf_counter()    

                # Loop to copy contents of incoming chunks to file, open file in write binary mode
                with open(file_path, "wb") as file:
                    print("\nDownloading file...\n")

                    firstTime = True

                    while True:

                        # Recieve data from client in chunks
                        data = self.client_socket.recv(1024)

                        if firstTime:
                            if METRIC:
                                firstTime = False
                                gotRequest = time.perf_counter()

                        # Escape sequence to run once end of file is reached
                        if b"<EOF>" in data:

                            if METRIC:
                                #record finshed upload time
                                finishedDownloadTime = time.perf_counter()

                            file.write(data.replace(b"<EOF>", b""))
                            print(f"Finished recieving file '{file_name}'.\n")
                            break
    
                        # Write data to open file
                        file.write(data)
            finally:
                file.close()

                if METRIC:
                    analysis.log_download_metircs(sendRequest,gotRequest,finishedDownloadTime,intialDownloadtime,os.path.abspath(file_name))

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
        self.safe_send(message)

        #wait for response from the server
        response = self.safe_recv(1024)

        #handlinlg the response from the server
        if response == str(self.incoming_codes['ok']):
            print(f"The file '{file_name}' has been successfully deleted from the server.\n")
        elif response == str(self.incoming_codes['file_DNE']):
            print(f"Failed to delete the file '{file_name}' from the server. This File might not exist.\n")

    # Desc: Make new directory in server
    # Auth: Spencer T. Robinson
    # Date: 11/21/24
    def make_directory_subroutine(self, folderName):
        file_path = self.s_cwd + '/' + folderName
        print(f"\nRequested a new directory named '{folderName}' be created.\n")

        message = f"{self.outgoing_codes['mkdir']} {file_path}"
        self.safe_send(message)

        #wait for response from the server
        response = self.safe_recv(1024)

        if response == str(self.incoming_codes['ok']):
            print(f"The directory '{file_path}', has been succcesfully created.\n")
        elif response == str(self.incoming_codes['dir_AE']):
            print(f"The directory '{folderName}', already exists.\n")

    # Desc: Delete a directory in server
    # Auth: Spencer T. Robinson
    # Date: 11/21/24
    def delete_directory_subroutine(self, folderName):
        file_path = self.s_cwd + '/' + folderName
        print(f"\nRequested the directory named '{folderName}' be deleted from the server.\n")

        message = f"{self.outgoing_codes['rmdir']} {file_path}"
        self.safe_send(message)

        #wait for response from the server
        response = self.safe_recv(1024)

        if response == str(self.incoming_codes['ok']):
            print(f"The directory '{file_path}', has been succcesfully deleted.\n")
        elif response == str(self.incoming_codes['dir_DNE']):
            print(f"The directory '{folderName}', does not exist.\n")

    # Desc: Change a directory in server
    # Auth: Spencer T. Robinson
    # Date: 11/21/24
    def change_directory_subroutine(self, folderName):
        
        if(folderName == ".."):
            file_path = os.path.dirname(self.s_cwd)
        else:
            file_path = self.s_cwd + '/' + folderName
        
        print(f"\nRequest to change the server directory...'.\n")

        message = f"{self.outgoing_codes['cd']} {file_path}"
        self.safe_send(message)

        #wait for response from the server
        response = self.safe_recv(1024)

        #adding a random comment to force commit condition
        if response == str(self.incoming_codes['ok']):
            print(f"The directory has been succcesfully changed.\n")
            self.s_cwd = file_path
        elif response == str(self.incoming_codes['dir_DNE']):
            print(f"The directory '{folderName}', does not exist.\n")
        elif response == str(self.incoming_codes['dir_top']):
            print(f"Unable to move up this directory.\n")

    # Desc: Prints current server directory in client 
    # Auth: Spencer T. Robinson
    # Date: 11/21/24
    def server_pwd(self):
        print(f"The current working directory of the server is '{self.s_cwd}'.\n")

    # Desc: Shorten the server directory to print on cli
    # Auth: Spencer T. Robinson
    # Date: 11/22/24
    def shorten_s_pwd(self):
        parent_dir = (os.path.dirname(self.s_cwd_constant))
        serverPWD = self.username + ": "
        startPos = len(str(parent_dir))+1
        while(startPos < len(self.s_cwd)):
            serverPWD += self.s_cwd[startPos]
            startPos += 1

        return serverPWD
        
    # Desc: Safe SEND and RECIEVE checks if the server is still active before sending
    # Auth: Lukas Kelk
    # Date: 11/23/24    
    def safe_send(self, message: str):
        try:
            self.client_socket.send(message.encode())
        except (socket.timeout,ConnectionResetError, socket.error):
            print("\nYou have been disconnected from the server.\n")
            self.authenticated = False
            self.client_socket.close()
            exit(1)

    #Desc: Safe SEND and RECIEVE checks if the server is still active before sending
    # Auth: Lukas Kelk
    # Date: 11/23/24  
    def safe_recv(self, buffer_size: int = 1024) -> str:
        try:
            response = self.client_socket.recv(buffer_size).decode()
            if not response:  # If server sends an empty response
                raise ConnectionResetError
            return response
        except (socket.timeout,ConnectionResetError, socket.error):
            print("\nYou timmed out and have been disconnected from the server.\n")
            self.authenticated = False
            self.client_socket.close()
            exit(1)