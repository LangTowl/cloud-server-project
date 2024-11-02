# client.py

import client_functions as cf
import getpass

if __name__ == "__main__":
    # Determine user status
    print("Client session started...\n\nDo you have an account? (y/n)")

    while True:
        account_status = input("> ")
        
        if account_status.lower() == "y":
            break
        elif account_status.lower() == "n":
            break
        else:
            print("Invalid input. Do you have an account? (y/n)")

    # Create unauthenticated client
    client = cf.Client()

    # If user has account, attempt sign in 
    while account_status == "y" and client.authenticated == False:
        # Collect user information
        username = input("\nEnter your username: ")
        password = getpass.getpass("\nEnter your password: ")

        # Initialize connection with server, attempt to authenticate
        client.init_client(username = username, password = password)

        # Break out of authentication loop if user is authenticated
        if client.authenticate_client() == True:
            break

        print("Do you want to try again, or make a new acount? (try/new)")
        failed = input("> ")

        if failed.lower() == "new":
            break
        elif failed.lower() == "try":
            continue
        else:
            print("Invalid input. Account couldn't be authenticated. Do you want to try again, or make a new acount? (try/new)")

        