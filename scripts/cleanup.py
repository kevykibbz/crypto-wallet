import os
import io
import sys
import dropbox
import requests
from dotenv import load_dotenv
import signal
import time

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

# Ensure standard output uses UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

# Load environment variables
ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')
TARGET_FOLDER = os.getenv('DROPBOX_TARGET_FOLDER')
TARGET_FOLDER_PATH = f'/{TARGET_FOLDER}/FileRequests'
PROCESSED_FOLDER_PATH = f'/{TARGET_FOLDER}/processed'
DOWNLOAD_FOLDER = './downloads'
JSON_FOLDER = './json'
CSV_FOLDER = './csv'  # Add this line for the CSV folder

# Initialize Dropbox client
dbx = dropbox.Dropbox(ACCESS_TOKEN)

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

def handle_signal(signum, frame):
    print("")
    print(f"\n> {RED}! [SIGNUM:{signum}] Terminating gracefully...{NC}")
    sys.stdout.flush()
    sys.exit(1)

# Set up signal handling for interrupt and termination signals
signal.signal(signal.SIGINT, handle_signal)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, handle_signal) # Handle termination signals

@network_check
def file_exists_in_dropbox(path):
    """Check if a file exists in Dropbox at the given path."""
    try:
        dbx.files_get_metadata(path)
        return True
    except dropbox.exceptions.ApiError as err:
        if isinstance(err.error, dropbox.files.GetMetadataError):
            return False
        else:
            raise

@network_check
def move_to_processed(file_name):
    """Move the specified file to the processed folder in Dropbox."""
    source_path = f'{TARGET_FOLDER_PATH}/{file_name}'
    destination_path = f'{PROCESSED_FOLDER_PATH}/{file_name}'
    
    if file_exists_in_dropbox(source_path):
        try:
            dbx.files_move_v2(source_path, destination_path, autorename=True)
            print(f"> {GREEN}✓{NC} Done(1).")
        except dropbox.exceptions.ApiError as err:
            print(f"> {RED}X{NC} Cleaning up failed.")
    else:
        print(f"> {RED}X{NC} {file_name} does not exist in {TARGET_FOLDER_PATH}.")
        
    print(" ")
    sys.stdout.flush()

@network_check
def cleanup_local_folder():
    """Delete all files in the local downloads folder."""
    for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
        for file in files:
            os.remove(os.path.join(root, file))
    print(f"> {GREEN}✓{NC} Done(2).")
    print("")
    sys.stdout.flush()

@network_check
def cleanup_json_folder():
    """Delete all files in the local json folder."""
    for root, dirs, files in os.walk(JSON_FOLDER):
        for file in files:
            os.remove(os.path.join(root, file))
    print(f"> {GREEN}✓{NC} Done(3).")
    print("")
    sys.stdout.flush()

@network_check
def cleanup_csv_folder():
    """Delete all files in the local csv folder."""
    for root, dirs, files in os.walk(CSV_FOLDER):
        for file in files:
            os.remove(os.path.join(root, file))
    print(f"> {GREEN}✓{NC} Done(4).")
    print("")
    sys.stdout.flush()

if __name__ == "__main__":
    # Get the list of downloaded files
    downloaded_files = os.listdir(DOWNLOAD_FOLDER)
    print(f"> {YELLOW}?{NC} Cleaning up...")
    print(" ")
    sys.stdout.flush()
    
    if not downloaded_files:
        print(f"> {RED}X{NC} No files found in the downloads folder.")
        print(" ")
        sys.stdout.flush()
    else:
        selected_file = downloaded_files[0]
        move_to_processed(selected_file)
    
    # Perform cleanup for local folder, JSON folder, and CSV folder
    cleanup_local_folder()
    cleanup_json_folder()
    cleanup_csv_folder()