import os
import json

def create_json_for_images(source_folder, target_folder):
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
      json_data["image"] = r"/data/local-files/?d=Project/Input_Images/"+filename

      # Create the JSON file
      s = image_name + ".json"
      json_file_path = os.path.join(target_folder, s)
      with open(json_file_path, "w") as f:
        json.dump(json_data, f, indent=4)

      print(f"Created JSON file for {filename} in {target_folder}")

# Replace these with your actual folder paths
source_folder = r"E:\task_2\Input_images"
target_folder = r"E:\task_2\json_file"

create_json_for_images(source_folder, target_folder)
