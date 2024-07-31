import os
import json
import signal
import sys
import io
import time
import requests

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

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

def validate_json_file(json_file_path):
    """Validate the JSON file by checking for specific keys with possible extra characters."""
    required_substrings = {"AMOUNT", "DATE"}

    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

            # Get the keys of the JSON file
            keys = data.keys()
            
            # Check if any of the required substrings are present in the keys
            valid = any(substring in key.upper() for key in keys for substring in required_substrings)
            
            if valid:
                print(f"\n{GREEN}> ✓ File is valid.{NC}")
                sys.stdout.flush()
                return True
            else:
                print(f"\n{RED}> X File is Invalid.{NC}")
                sys.stdout.flush()
                return False
    except (json.JSONDecodeError, IOError) as e:
        print(f"File {json_file_path}: Invalid (Error: {e})")
        sys.stdout.flush()
        return False

@network_check
def validate_json_files_in_folder(folder_path):
    """Validate all JSON files in the given folder."""
    all_valid = True
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith('.json'):
            json_file_path = os.path.join(folder_path, file_name)
            if not validate_json_file(json_file_path):
                all_valid = False
    return all_valid

if __name__ == "__main__":
    json_dir = './json'
    print(f"{YELLOW}> ? Validating file... {NC}")
    sys.stdout.flush()
    if not validate_json_files_in_folder(json_dir):
        sys.exit(1)  # Exit with status 1 if any file is invalid
    sys.exit(0)  # Exit with status 0 if all files are valid