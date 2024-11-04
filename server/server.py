# server.py

import server_functions as sf
import threading

if __name__ == "__main__":
    # Create and initialize server object
    server = sf.Server()
    server.init_server()

    # Continually listen for new client connections
    while True:
        client_socket, client_address = server.server_socket.accept()
        print(f"\nConnection from {client_address} has been established.\n")

        # Create a new thread to handle client connections
        client_thread = threading.Thread(target=server.incoming_client_communications, args=(client_socket,))
        client_thread.start()
