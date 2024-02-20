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


def compare_snapshots_and_save_correct_csv(snapshot1, snapshot2, correct_csv_file_path,incorrct_csv_file_path,mismatch_path):
    # Load annotations from snapshots
    with open(snapshot1, 'r') as file:
        annotations_annotator_1 = json.load(file)
    with open(snapshot2, 'r') as file:
        annotations_annotator_2 = json.load(file)

    # Initialize lists to store correct and mismatched file paths
    correct_file_paths = []
    mismatched_file_paths = []
    prime_match = []

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
            prime_match.append([ann1['image'], text1,text2])

    file_exists = os.path.isfile(correct_csv_file_path)
    # Save correct file paths and annotations to a CSV file
    with open(correct_csv_file_path, 'a' if file_exists else 'w' , newline='') as file:
        writer = csv.writer(file)
        writer.writerows(correct_file_paths)
    # Save correct file paths and annotations to a CSV file
    with open(incorrect_csv_file_path, 'w' , newline='') as file:
        writer = csv.writer(file)
        writer.writerows(prime_match)
    
    # Save mismatched file paths to a JSON file
    mismatched_data = [{'file_path': path[0]} for path in mismatched_file_paths]
    with open(mismatch_path, 'w') as file:
        json.dump(mismatched_data, file, indent=4)

    return mismatched_file_paths

def compare_and_resolve_mismatches(snapshot1, correct_csv_file_path, incorrect_csv_file_path, mismatch_path):
    """
    Compares annotations from a snapshot with prior mismatches and iteratively searches
    for a correct text among subsequent snapshots provided.

    Args:
        snapshot1 (str): Path to the first snapshot file (JSON format).
        correct_csv_file_path (str): Path to the CSV file containing correct annotations.
        incorrect_csv_file_path (str): Path to the CSV file containing prior mismatches.
        mismatch_path (str): Path to the JSON file to store remaining mismatches.
        
    Returns:
        list: A list of dictionaries containing information about unresolved mismatches,
              including file path, all compared texts, and a flag indicating resolution.
    """

    # Load annotations from the first snapshot
    with open(snapshot1, 'r') as file:
        annotations_annotator_1 = json.load(file)

    # Load prior mismatches from the CSV file
    with open(incorrect_csv_file_path, 'r') as file:
        reader = csv.reader(file)
        prior_mismatches = list(reader)

    # Initialize lists to store resolved and unresolved mismatches
    resolved_mismatches = []
    unresolved_mismatches = [{"file_path": path[0], "texts": path[1:]} for path in prior_mismatches]

    # Iterate through subsequent snapshots, comparing with prior texts
    with open(snapshot_path, 'r') as file:
        annotations_current = json.load(file)

    for i, mismatch in enumerate(unresolved_mismatches):
        image_path = mismatch["file_path"]
        mismatch_texts = mismatch["texts"]

        # Extract current annotator's text
        current_text = annotations_current[0]['transcription']

        # Check if any existing mismatch text or the current text matches
        is_resolved = any(text == current_text for text in mismatch_texts)

        if is_resolved:
            # Match found, add to resolved list and remove from unresolved
            resolved_mismatches.append([image_path, current_text])
            unresolved_mismatches.pop(i)
        else:
            mismatch_texts.append(current_text)

            # Check if the image_path already exists in the CSV
            with open(incorrect_csv_file_path, 'r') as file:
                reader = csv.reader(file)
                existing_rows = [row for row in reader if row[0] == image_path]

            if existing_rows:
                # Image path found, append the new text as a column
                with open(incorrect_csv_file_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([*existing_rows[0][1:], current_text])
            else:
                # Image path not found, create a new row
                with open(incorrect_csv_file_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([image_path, *mismatch_texts])

    # Append resolved mismatches to the correct CSV file
    with open(correct_csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(resolved_mismatches)

    # Save remaining mismatches to the JSON file
    with open(mismatch_path, 'w') as file:
        json.dump(unresolved_mismatches, file, indent=4)

    return unresolved_mismatches
