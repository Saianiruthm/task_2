from main import compare_snapshots_and_save_correct_csv,import_tasks_from_json
from label_studio_sdk import Client,Project
import time
import os

# Define the Label Studio API keys and URLs for both annotators
API_KEY_ANNOTATOR_1 = 'API'
API_KEY_ANNOTATOR_2 = 'API'
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

project_1.delete_all_tasks()
project_2.delete_all_tasks()

json_file_path = r"E:\task_2\json_mismatch_file"

#Import Tasks
import_tasks_from_json(project_1, json_file_path)
#import_tasks_from_json(project_2, json_file_path)



