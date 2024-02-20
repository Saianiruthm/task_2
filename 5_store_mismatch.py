import os
import json

input_json = 'mismatched.json'
with open(input_json) as inp:
    tasks = json.load(inp)
target = r"E:\task_2\json_mismatch_file"

for i,v in enumerate(tasks):
    p = "task_"+ str(i)
    s = p + ".json";
    # Create empty JSON data
    json_data = {}
    # Add image path to the data (you can add more information if needed)
    json_data["image"] = v['file_path']
    print(json_data)
    filename = os.path.join(target, s)
    with open(filename, "w") as f:
        json.dump(json_data, f, indent=4)

    print(f"Created JSON file for {filename} in {target}")

