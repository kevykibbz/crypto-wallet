import time
import dropbox
from dropbox.exceptions import AuthError, ApiError
from dotenv import load_dotenv
import os
import sys
import io
import signal
import requests

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

load_dotenv()

# Ensure standard output uses UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Define the .env file path
ENV_FILE = '../.env'

# Global flag to track network connectivity status
network_good = False

# Retrieve the current access token from .env
ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

def handle_signal(signum, frame):
    print("")
    sys.stdout.flush()
    print(f"\n> {RED}! [SIGNUM:{signum}] Terminating gracefully...{NC}")
    sys.stdout.flush()
    sys.exit(1)

# Set up signal handling for interrupt and termination signals
signal.signal(signal.SIGINT, handle_signal)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, handle_signal) # Handle termination signals

def network_check(func):
    """Decorator to check network connectivity before executing the function."""
    def wrapper(*args, **kwargs):
        global network_good
        global check_internet
        if not network_good:
            for attempt in range(5):
                try:
                    # Check network connectivity
                    response = requests.get("https://google.com", timeout=10)
                    response.raise_for_status()
                    if not network_good:
                        print("")
                        sys.stdout.flush()
                        print(f"{GREEN}✓ Network connectivity is good.{NC}")
                        sys.stdout.flush()
                        print("")
                        sys.stdout.flush()
                        network_good = True
                    # Network is good, proceed with the function
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, requests.exceptions.ConnectTimeout) as e:
                    print(f"{RED}X Network connectivity issue detected.{NC}")
                    sys.stdout.flush()
                    print("")
                    sys.stdout.flush()
                    print(f"{YELLOW}? Attempting to reconnect... (Attempt {attempt + 1}/5){NC}")
                    sys.stdout.flush()
                    time.sleep(5)
            print(f"{RED}X Maximum retry attempts reached. Exiting.{NC}")
            sys.stdout.flush()
            sys.exit(1)
        else:
            # Network is already confirmed to be good, proceed with the function
            return func(*args, **kwargs)
    return wrapper

@network_check
def validate_access_token(token):
    """Validate the Dropbox access token."""
    try:
        dbx = dropbox.Dropbox(token)
        dbx.users_get_current_account()
        print(f"{GREEN}✓ Access token is valid.{NC}")
        sys.stdout.flush()
        print("")
        sys.stdout.flush()
        return True
    except AuthError:
        print(f"{RED}X Access token is invalid or expired.{NC}")
        sys.stdout.flush()
        print("")
        sys.stdout.flush()
        return False

def prompt_for_new_token():
    """Prompt the user to enter a new access token."""
    new_token = input(f"{YELLOW}? Please enter a new access token: {NC}")
    return new_token

def update_env_file(key, value):
    """Update the .env file with the new access token."""
    if not os.path.exists(ENV_FILE):
        print(f"\n> {RED}! Target path not found. Exiting...{NC}")
        sys.stdout.flush()
        print("")
        sys.stdout.flush()
        sys.exit(1)
    else:
        # Update the .env file with the new access token
        print("")
        sys.stdout.flush()
        print(f"{CYAN}? Updating environment...{NC}")
        sys.stdout.flush()
        print("")
        sys.stdout.flush()

        # Read the existing contents of the .env file
        with open(ENV_FILE, 'r') as file:
            lines = file.readlines()

        # Update the line if the key exists, otherwise add a new line
        updated = False
        with open(ENV_FILE, 'w') as file:
            for line in lines:
                if line.startswith(f"{key}="):
                    file.write(f"{key}={value}\n")
                    updated = True
                else:
                    file.write(line)
            if not updated:
                file.write(f"{key}={value}\n")

        print(f"{GREEN}✓ Access token updated successfully.{NC}")
        sys.stdout.flush()
        print("")
        sys.stdout.flush()

@network_check
def connect_to_dropbox():
    """Connect to Dropbox and perform operations."""
    global ACCESS_TOKEN
    
    if not ACCESS_TOKEN:
        print(f"{RED}X Access token not set.{NC}")
        sys.stdout.flush()
        print("")
        sys.stdout.flush()
        sys.exit(1)
    
    try:
        dbx = dropbox.Dropbox(ACCESS_TOKEN)
        dbx.users_get_current_account()
        print(f"{GREEN}✓ Dropbox connection established.{NC}")
        sys.stdout.flush()
        print("")
        sys.stdout.flush()
    except AuthError:
        print(f"{RED}X Wrong or expired access token. Please try again.{NC}")
        sys.stdout.flush()
        print("")
        sys.stdout.flush()
        # Prompt for a new token and update .env
        new_token = prompt_for_new_token()
        update_env_file('DROPBOX_ACCESS_TOKEN', new_token)
        ACCESS_TOKEN = new_token  # Update the global variable
        # Retry connecting with the new token
        connect_to_dropbox()

if __name__ == "__main__":
    if not validate_access_token(ACCESS_TOKEN):
        new_token = prompt_for_new_token()
        update_env_file('DROPBOX_ACCESS_TOKEN', new_token)
        # Update the global variable and retry connection
        ACCESS_TOKEN = new_token
        connect_to_dropbox()
    else:
        connect_to_dropbox()