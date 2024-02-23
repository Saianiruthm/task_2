import csv
import json
from label_studio_sdk import Client
import time
import os
import requests
from typing import List


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


def compare_snapshots_and_save_correct_csv(snapshot1, snapshot2, correct_csv_file_path,incorrect_json_file_path,mismatch_path):
    # Load annotations from snapshots
    with open(snapshot1, 'r') as file:
        annotations_annotator_1 = json.load(file)
    with open(snapshot2, 'r') as file:
        annotations_annotator_2 = json.load(file)

    # Initialize lists to store correct and mismatched file paths
    correct_file_paths = []
    mismatched_file_paths = []
    mismatched_data = {}
    
    # Compare text annotations from both snapshots
    for ann1, ann2 in zip(annotations_annotator_1, annotations_annotator_2):
        # Extract text values from the results
        text1 = [ann1['transcription']]  # Assuming single text value per annotation
        text2 = [ann2['transcription']]  # Assuming single text value per annotation

        # Compare the text values
        if text1 == text2:
            # If the text annotations match, add the file path to the correct list
            correct_file_paths.append([ann1['image'], *text1])
        else:
            # If there is a mismatch, add the file path to the mismatched list
            mismatched_file_paths.append(ann1['image'])
            mismatched_data[ann1['image']]= [*text1, *text2]

    file_exists = os.path.isfile(correct_csv_file_path)
    # Save correct file paths and annotations to a CSV file
    with open(correct_csv_file_path, 'w' , newline='') as file:
        writer = csv.writer(file)
        writer.writerows(correct_file_paths)
    # Save correct file paths and annotations to a CSV file
    with open(incorrect_json_file_path, 'w') as file:
        json.dump(mismatched_data, file, indent=4)
    
    # Save mismatched file paths to a JSON file
    mismatched_datas = [{'file_path': path} for path in mismatched_file_paths]
    with open(mismatch_path, 'w') as file:
        json.dump(mismatched_datas, file, indent=4)

    return mismatched_file_paths

def compare_and_resolve_mismatches(snapshot_path, correct_csv_file_path, incorrect_json_file_path, mismatch_path):
    """
    Compares annotations, updates mismatches, and adds resolved ones to correct annotations.

    Args:
        snapshot_path (str): Path to the snapshot file (JSON format).
        correct_csv_file_path (str): Path to the correct annotations CSV file.
        incorrect_json_file_path (str): Path to the mismatched annotations JSON file.
        mismatch_path (str): Path to the JSON file to store remaining mismatches.

    Returns:
        list: A list of dictionaries containing information about unresolved mismatches.
    """

    # Load annotations from snapshot and mismatched JSON
    with open(snapshot_path, 'r') as file:
        annotations_current = json.load(file)
    with open(incorrect_json_file_path, 'r') as file:
        mismatched_data = json.load(file)
        print(type(mismatched_data))
        print(mismatched_data)

    # Create a dictionary for efficient lookup by file path
    filepath_to_mismatches = {file_path: texts for file_path, texts in mismatched_data.items()}
    
    # Iterate through annotations, check for match, update or add to correct annotations
    resolved_mismatches = []
    unresolved_mismatches = []

    for annotation in annotations_current:
        current_image_path = annotation["image"]
        current_text = annotation["transcription"]

        mismatch_texts = filepath_to_mismatches.get(current_image_path, [])

        # Check if a match is found
        is_matched = any(text == current_text for text in mismatch_texts)

        if is_matched:
            # Match found, remove matched text from mismatches and add resolved entry
            resolved_mismatches.append([current_image_path,current_text])
            del filepath_to_mismatches[current_image_path]  # Remove the entire dictionary
        else:
            # No match found, append current text to mismatches with appropriate index
            new_text_index = len(mismatch_texts) + 1
            new_text_key = f"text_{new_text_index}"
            mismatch_texts.append(current_text)
            filepath_to_mismatches[current_image_path] = mismatch_texts
            unresolved_mismatches.append({
                "file_path": current_image_path
            })

    # Update incorrect_json_file_path with modified mismatches
    with open(incorrect_json_file_path, 'w') as file:
        json.dump(filepath_to_mismatches, file, indent=4)

    # Append resolved mismatches to the correct CSV file
    with open(correct_csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(resolved_mismatches)

    # Save remaining mismatches to the JSON file
    with open(mismatch_path, 'w') as file:
        json.dump(unresolved_mismatches, file, indent=4)

    return unresolved_mismatches
