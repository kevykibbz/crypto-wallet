import io
import os
import sys
import time
import requests
import signal
from dotenv import load_dotenv

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color
YELLOW = '\033[1;33m'
CYAN = '\033[0;36m'

# Load environment variables
load_dotenv()

DROPBOX_ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')
DROPBOX_TARGET_FOLDER = os.getenv('DROPBOX_TARGET_FOLDER')

# Ensure standard output uses UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def handle_signal(signum, frame):
    print("")
    print(f"\n> {RED}! [SIGNUM:{signum}] Terminating gracefully...{NC}")
    sys.stdout.flush()
    sys.exit(1)

# Set up signal handling for interrupt and termination signals
signal.signal(signal.SIGINT, handle_signal)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, handle_signal) # Handle termination signals

def network_check(func):
    """Decorator to check network connectivity before executing the function."""
    def wrapper(*args, **kwargs):
        for attempt in range(5):
            try:
                response = requests.get("https://google.com", timeout=10)
                response.raise_for_status()
                return func(*args, **kwargs)
            except (requests.exceptions.RequestException, requests.exceptions.ConnectTimeout) as e:
                print(f"{YELLOW}> ? Attempting to reconnect... (Attempt {attempt + 1}/5){NC}")
                sys.stdout.flush()
                time.sleep(5)
        print(f"{RED}> X Maximum retry attempts reached. Exiting.{NC}")
        sys.stdout.flush()
        sys.exit(1)
    return wrapper

@network_check
def create_folder_if_not_exists(folder_name):
    """Create a folder in Dropbox if it does not exist."""
    url = "https://api.dropboxapi.com/2/files/create_folder_v2"
    headers = {
        "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "path": f"/{folder_name}",
        "autorename": False
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"{YELLOW}>  Checking Folder availability...{NC}")
    print("")
    if response.status_code == 409:
        # Folder already exists
        print(f"{CYAN}> ! Folder '{folder_name}' located.{NC}")
        print("")
    elif response.status_code == 200:
        # Folder created successfully
        print(f"{YELLOW}>  Creating folder..{NC}")
        print("")
        print(f"{GREEN}> [OK] Folder '{folder_name}' created successfully.{NC}")
        print("")
    else:
        print(f"{RED}> ! Error creating folder '{folder_name}': {response.text}{NC}")
        print("")
    sys.stdout.flush()

if __name__ == "__main__":
    create_folder_if_not_exists(DROPBOX_TARGET_FOLDER)