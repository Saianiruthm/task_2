import os
import json
import shutil

def create_json_for_images(source_folder, target_folder,Project_name):
  """
  Creates a JSON file in a separate folder for each image in a specified source folder.

  Args:
      source_folder: The path to the folder containing the images.
      target_folder: The path to the folder where the JSON files will be created.
  """

  for filename in os.listdir(source_folder):
    if filename.endswith((".jpg", ".jpeg", ".png")):
      image_path = os.path.join(source_folder, filename)

      # Extract image name without extension
      image_name = os.path.splitext(filename)[0]

      # Create empty JSON data
      json_data = {}

      # Add image path to the data (you can add more information if needed)
      json_data["image"] = r"/data/local-files/?d="+ Project_name+r"/Input_Images/"+filename

      # Create the JSON file
      s = image_name + ".json"
      json_file_path = os.path.join(target_folder, s)
      with open(json_file_path, "w") as f:
        json.dump(json_data, f, indent=4)

      print(f"Created JSON file for {filename} in {target_folder}")


def create_directory(path):
     """
    Creates a new directory at the specified path.

    Args:
        path (str): The full path of the directory to create.

    Raises:
        OSError: If there's an error creating the directory (e.g., permission issues).
    """
    try:
        os.makedirs(path)
        print(f"Directory '{path}' created successfully")
    except FileExistsError:
        print(f"Directory '{path}' already exists")


def copy_directory(src_path, dst_path):
    """
    Copies a directory and its contents from the source path to the destination path.

    Args:
        src_path (str): The full path of the source directory to copy.
        dst_path (str): The full path of the destination directory to create.

    Raises:
        OSError: If there's an error copying the directory or its contents.
    """
    try:
        shutil.copytree(src_path, dst_path)
        print(f"Directory '{src_path}' copied to '{dst_path}' successfully")
    except FileExistsError:
        print(f"Directory '{dst_path}' already exists")

