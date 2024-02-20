import csv
import json
from label_studio_sdk import Client
import time
import os
import requests

def register_local_folder(api_token, project, paths, titles):
    """
    Registers a local folder as a storage in Label Studio.

    Args:
        api_token: Your API token for authorization.
        project: The project to sync with.
        path: The local path to sync from.
        title: The title for the local storage.
    """
    # Register a local folder as storage
    storage = project.connect_local_import_storage(
        local_store_path= paths,
        title= titles,
        description='Creating Local Storage',
        regex_filter='.*',  # Optional: regex to filter files
        use_blob_urls=True  # Optional: interpret objects as BLOBs and generate URLs
    )

    # Check if the storage was added successfully
    if storage:
        print(f"Storage '{storage['title']}' registered successfully with ID: {storage['id']}")
        return storage
    else:
        print("Failed to register storage.")

#Function To store project_id
def store_id(file,txt_1,txt_2):
    file_exists = os.path.isfile(file)
    with open(file, 'w') as f:
        f.write(str(txt_1) + "\n")
        f.write(str(txt_2) + "\n")


#Function to create project
def create_project(ls,pt):
    project = ls.start_project(
        title= str(pt),
        label_config='''
        <View>
            <Header value="View the image carefully" />
            <Image name="Image" value="$image"/>
            <Header value="Write the transcription" />
            <TextArea name="transcription" toName="Image"
                rows="1" editable="true" maxSubmissions="1" />
        </View>
        '''
    )
    return project


    
def import_tasks_from_json(project, folder_path):
    """
    Imports tasks from individual JSON files within a specified folder.

    Args:
        project: The Label Studio project object.
        folder_path: The path to the folder containing the JSON task files.
    """

    json_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".json")]

    for json_file in json_files:
        with open(json_file, 'r') as file:
            task = json.load(file)
            project.import_tasks([task])  # Import a single task at a time


def compare_snapshots_and_save_correct_csv(snapshot1, snapshot2, correct_csv_file_path,mismatch_path):
    # Load annotations from snapshots
    with open(snapshot1, 'r') as file:
        annotations_annotator_1 = json.load(file)
    with open(snapshot2, 'r') as file:
        annotations_annotator_2 = json.load(file)

    # Initialize lists to store correct and mismatched file paths
    correct_file_paths = []
    mismatched_file_paths = []

    # Compare text annotations from both snapshots
    for ann1, ann2 in zip(annotations_annotator_1, annotations_annotator_2):
        # Extract text values from the results
        text1 = [ann1['transcription']]  # Assuming single text value per annotation
        text2 = [ann2['transcription']]  # Assuming single text value per annotation

        # Compare the text values
        if text1 == text2:
            # If the text annotations match, add the file path to the correct list
            correct_file_paths.append([ann1['image'], text1])
        else:
            # If there is a mismatch, add the file path to the mismatched list
            mismatched_file_paths.append([ann1['image']])

    file_exists = os.path.isfile(correct_csv_file_path)
    # Save correct file paths and annotations to a CSV file
    with open(correct_csv_file_path, 'a' if file_exists else 'w' , newline='') as file:
        writer = csv.writer(file)
        writer.writerows(correct_file_paths)

    # Save mismatched file paths to a JSON file
    mismatched_data = [{'file_path': path[0]} for path in mismatched_file_paths]
    with open(mismatch_path, 'w') as file:
        json.dump(mismatched_data, file, indent=4)

    return mismatched_file_paths

