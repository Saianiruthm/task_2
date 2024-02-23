import csv
import json
from label_studio_sdk import Client
import time
import os
from main import *
from to_json import *
import shutil


name = input("Enter name of the project: ")
#Create storage for cloud
# Replace these with your actual folder paths
source_folder = r"E:\task_2\Input_images"
target_folder = r"E:\task_2\json_file"
create_json_for_images(source_folder, target_folder,name)
path_1 = r'C:\data\media\Project'
path_2 = os.path.join(path_1, name)
create_directory(path_2)
dst_path = os.path.join(path_2, r'Input_Images')
copy_directory(source_folder, dst_path)

#For community users:
# Define the Label Studio API keys and URLs for both annotators
API_KEY_ANNOTATOR_1 = 'API'
API_KEY_ANNOTATOR_2 = 'API'
LABEL_STUDIO_URL = 'http://localhost:8080/'

"""
For Enterprise:
# Define the Label Studio API keys and URLs for both annotators
API_KEY_ANNOTATOR_1 = 'API'
API_KEY_ANNOTATOR_2 = 'API'
LABEL_STUDIO_URL = 'https://app.heartex.com/'
"""

# Initialize the Label Studio clients for both annotators
client_1 = Client(url=LABEL_STUDIO_URL, api_key=API_KEY_ANNOTATOR_1)
client_2 = Client(url=LABEL_STUDIO_URL, api_key=API_KEY_ANNOTATOR_2)

# Main workflow
json_file_path = r"E:\task_2\json_file"
project_name_1 = name + '_1'
project_name_2 = name + '_2'
project_1 = create_project(client_1,project_name_1)
project_2 = create_project(client_2,project_name_2)
store_id("ids.txt",project_1.id,project_2.id)

#Create Storage
title = "Storage"
storage_info_1 = register_local_folder(API_KEY_ANNOTATOR_1, project_1, path_1, title)
storage_info_2 = register_local_folder(API_KEY_ANNOTATOR_2, project_2, path_1, title)
storage_id_1 = storage_info_1['id']
storage_id_2 = storage_info_2['id']

#Import Tasks
import_tasks_from_json(project_1, json_file_path)
import_tasks_from_json(project_2, json_file_path)

