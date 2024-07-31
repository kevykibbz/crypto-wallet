import io
import sys
import boto3
import os
import time
import json
import pandas as pd
from dotenv import load_dotenv
import requests
import signal

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color
YELLOW = '\033[1;33m'
CYAN = '\033[0;36m'

# Initialize the environment
load_dotenv()

# Ensure standard output uses UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET = os.getenv('S3_BUCKET')

# Initialize boto3 clients
s3_client = boto3.client('s3',
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                         region_name=AWS_REGION)

textract_client = boto3.client('textract',
                               aws_access_key_id=AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                               region_name=AWS_REGION)

# Directory containing the files to upload and analyze
downloads_dir = '../downloads'
json_dir = '../json'
csv_dir = '../csv'

# Ensure the JSON and CSV directories exist
os.makedirs(json_dir, exist_ok=True)
os.makedirs(csv_dir, exist_ok=True)

# Get the first file in the downloads directory
file_list = os.listdir(downloads_dir)
if not file_list:
    print("No files found in the downloads directory.")
    sys.stdout.flush()
    exit(1)

local_file_path = os.path.join(downloads_dir, file_list[0])
s3_key = file_list[0]

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
def upload_file_to_s3(file_path, bucket, key):
    """Upload the file to S3."""
    s3_client.upload_file(file_path, bucket, key)

@network_check
def start_textract_job():
    """Start Textract job."""
    response = textract_client.start_document_analysis(
        DocumentLocation={'S3Object': {'Bucket': S3_BUCKET, 'Name': s3_key}},
        FeatureTypes=['FORMS']
    )
    return response['JobId']

@network_check
def get_textract_job_status(job_id):
    """Check the status of the Textract job."""
    response = textract_client.get_document_analysis(JobId=job_id)
    return response

def fetch_textract_results(job_id):
    """Fetch the results of the Textract job."""
    results = []
    next_token = None
    while True:
        response = textract_client.get_document_analysis(JobId=job_id, NextToken=next_token) if next_token else textract_client.get_document_analysis(JobId=job_id)
        results.extend(response['Blocks'])
        next_token = response.get('NextToken')
        if not next_token:
            break
    return results

# Upload the file to S3 with network check
upload_file_to_s3(local_file_path, S3_BUCKET, s3_key)

# Start Textract job with network check
job_id = start_textract_job()
print("")
print(f"{YELLOW}> ? Started job with ID: {job_id}{NC}\n")
sys.stdout.flush()

# Wait for the job to complete
while True:
    status = get_textract_job_status(job_id)['JobStatus']
    if status in ['SUCCEEDED', 'FAILED']:
        break
    print(f"{CYAN}> ! Job status: {status}{NC}\n")
    sys.stdout.flush()
    time.sleep(5)

if status == 'SUCCEEDED':
    print(f"{GREEN}> [OK] Job succeeded.{NC}\n")
    sys.stdout.flush()

    # Get the results
    blocks = fetch_textract_results(job_id)
    
    # Process the results
    key_map = {}
    value_map = {}
    block_map = {}
    
    # Gather the blocks
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == 'KEY_VALUE_SET':
            if 'KEY' in block['EntityTypes']:
                key_map[block_id] = block
            else:
                value_map[block_id] = block

    # Find key-value pairs
    def get_kv_relationship(key_map, value_map, block_map):
        kvs = {}
        for block_id, key_block in key_map.items():
            key = ''
            if 'Relationships' in key_block:
                for relationship in key_block['Relationships']:
                    if relationship['Type'] == 'CHILD':
                        for child_id in relationship['Ids']:
                            word = block_map[child_id]
                            if word['BlockType'] == 'WORD':
                                key += word['Text'] + ' '
                            elif word['BlockType'] == 'SELECTION_ELEMENT':
                                if word['SelectionStatus'] == 'SELECTED':
                                    key += 'X '
            key = key.strip().upper()  # Capitalize the key
            if 'Relationships' in key_block:
                for relationship in key_block['Relationships']:
                    if relationship['Type'] == 'VALUE':
                        for value_id in relationship['Ids']:
                            value_block = value_map[value_id]
                            value = ''
                            if 'Relationships' in value_block:
                                for relationship in value_block['Relationships']:
                                    if relationship['Type'] == 'CHILD':
                                        for child_id in relationship['Ids']:
                                            word = block_map[child_id]
                                            if word['BlockType'] == 'WORD':
                                                value += word['Text'] + ' '
                                            elif word['BlockType'] == 'SELECTION_ELEMENT':
                                                if word['SelectionStatus'] == 'SELECTED':
                                                    value += 'X '
                            value = value.strip()
                            kvs[key] = value
        return kvs

    kv_pairs = get_kv_relationship(key_map, value_map, block_map)

    # Save the key-value pairs to a JSON file
    json_file_path = os.path.join(json_dir, f"{os.path.splitext(file_list[0])[0]}.json")
    with open(json_file_path, 'w') as json_file:
        json.dump(kv_pairs, json_file, indent=4)
    print(f"{GREEN}> [OK] File successfully converted to JSON and saved at {json_file_path}{NC}")
    print("")
    sys.stdout.flush()
    
    # Convert JSON to CSV
    df = pd.DataFrame.from_dict(kv_pairs, orient='index', columns=['Value'])
    csv_file_path = os.path.join(csv_dir, f"{os.path.splitext(file_list[0])[0]}.csv")
    df.to_csv(csv_file_path, index_label='Key')
    print(f"{GREEN}> [OK] File successfully converted to CSV and saved at {csv_file_path}{NC}")
    print("")
    sys.stdout.flush()

    print(f"{GREEN}> [OK] Finalizing...{NC}\n")
    sys.stdout.flush()

else:
    print(f"{RED}> ! Job failed with status: {status}{NC}\n")
    sys.stdout.flush()