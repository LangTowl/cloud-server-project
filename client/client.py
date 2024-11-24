# client.py

import client_functions as cf
import getpass

if __name__ == "__main__":
    # Determine user status
    print("Client session started...\n\nDo you have an account? (y/n)\n")

    while True:
        account_status = input("> ")
        
        if account_status.lower() == "y":
            break
        elif account_status.lower() == "n":
            break
        else:
            print("\nInvalid input. Do you have an account? (y/n)\n")

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
            account_status = "n"
            break
        elif failed.lower() == "try":
            continue
        else:
            print("Invalid input. Account couldn't be authenticated. Do you want to try again, or make a new acount? (try/new)")

    # If user does not have an account, prompt them to create one
    while account_status == "n" and client.authenticated == False:
        # Collect user information
        username = input("\nChoose a username: ")
        password = getpass.getpass("\nChoose a password: ")
        password_confirm = getpass.getpass("\nConfirm password: ")

        # Prompt user to resubmit password if passwords do not match
        if password != password_confirm:
            print("\nPasswords do not match, please try again.")
            continue

        # Initialize connection with server, attempt to authenticate
        client.init_client(username = username, password = password)

        # Attempt to authorize new client with server
        client.athorize_new_client()

        # Break out of authentication loop if user is authenticated
        if client.authenticate_client() == True:
            break

        print("Do you want to try again? (y/n)")
        failed = input("> ")

        if failed.lower() == "n":
            break
        elif failed.lower() == "y":
            continue
        else:
            print("Invalid input. Account couldn't be authenticated. Do you want to try again, or make a new acount? (try/new)")
    
    # Code to run once user is authenticated
    while True:
        if client.authenticated == False:
            break

        command = input(f"{client.shorten_s_pwd()} > ")

        # Check to see if user input is a valid command
        valid_command = client.validate_command(command)

        # If valid, pass instruction to command handler
        if valid_command == True:
            client.direct_outgoing_commands(command)

        # Else, prompt user to retry 
        else:
            try_again = input("Do you want to try again? (y/n): ")

            if try_again.lower() == 'y':
                continue
            elif try_again.lower() == 'n':
                break
            else:
                print("Unrecognized command entered.\n")