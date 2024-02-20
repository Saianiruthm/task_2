import csv
import json
from label_studio_sdk import Client
import time
import os
from main import *
name = input("Enter name of the project: ")
#For community users:
# Define the Label Studio API keys and URLs for both annotators
API_KEY_ANNOTATOR_1 = '68a3fcdd73a7801d83b42e29920cdbf90af50dfd'
API_KEY_ANNOTATOR_2 = '95e9a6c97d84ed0520f65fc3af3972d628c6986f'
LABEL_STUDIO_URL = 'http://localhost:8080/'

"""
For Enterprise:
# Define the Label Studio API keys and URLs for both annotators
API_KEY_ANNOTATOR_1 = 'e212d485a42bae85b2ddc97dc210441613340acd'
API_KEY_ANNOTATOR_2 = 'bd5a69e09b89256f8d9232d01a4b710846b12eb8'
LABEL_STUDIO_URL = 'https://app.heartex.com/'
"""

# Initialize the Label Studio clients for both annotators
client_1 = Client(url=LABEL_STUDIO_URL, api_key=API_KEY_ANNOTATOR_1)
client_2 = Client(url=LABEL_STUDIO_URL, api_key=API_KEY_ANNOTATOR_2)

# Main workflow
json_file_path = r"E:\task_2\json_file"
path = r'C:\data\media\Project'
project_name_1 = name + '_1'
project_name_2 = name + '_2'
project_1 = create_project(client_1,project_name_1)
project_2 = create_project(client_2,project_name_2)
store_id("ids.txt",project_1.id,project_2.id)

#Create Storage
title = 'Directory'
storage_info_1 = register_local_folder(API_KEY_ANNOTATOR_1, project_1, path, title)
storage_info_2 = register_local_folder(API_KEY_ANNOTATOR_2, project_2, path, title)
storage_id_1 = storage_info_1['id']
storage_id_2 = storage_info_2['id']

#Import Tasks
import_tasks_from_json(project_1, json_file_path)
import_tasks_from_json(project_2, json_file_path)

