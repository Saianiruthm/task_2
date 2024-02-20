from main import compare_snapshots_and_save_correct_csv
from label_studio_sdk import Client,Project
import time
import os

# Define the Label Studio API keys and URLs for both annotators
API_KEY_ANNOTATOR_1 = 'API_1'
API_KEY_ANNOTATOR_2 = 'API_2'
LABEL_STUDIO_URL = 'http://localhost:8080/'

# Initialize the Label Studio clients for both annotators
client_1 = Client(url=LABEL_STUDIO_URL, api_key=API_KEY_ANNOTATOR_1)
client_2 = Client(url=LABEL_STUDIO_URL, api_key=API_KEY_ANNOTATOR_2)

#Get project from project id
with open('ids.txt', 'r') as f:
    lines = f.readlines()
project_1_id = int(lines[0].strip())
project_2_id = int(lines[1].strip())

project_1 = Project.get_from_id(client_1, project_1_id)
project_2 = Project.get_from_id(client_2, project_2_id)

# Create and download snapshots for both annotators
project_1.export_tasks( export_type= 'JSON_MIN',download_all_tasks = False,export_location = "project_1.json")
project_2.export_tasks( export_type= 'JSON_MIN',download_all_tasks = False,export_location = "project_2.json")


# Call the function with the appropriate file paths
mismatched_paths = compare_snapshots_and_save_correct_csv(
    'project_1.json',
    'project_2.json',
    'correct_annotations.csv',
    'mismatched.json'
)

# Output the mismatched paths for verification
print(f"Mismatched file paths: {mismatched_paths}")

