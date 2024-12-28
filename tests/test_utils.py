import os
import json


def load_json_from_file(file_path) -> dict | list:
    print(file_path)
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def load_json_files_with_prefix(
    target_folder: str, prefix: str = ""
) -> list[tuple[dict | list, str]]:
    """Gets all json files in @target_folder with specified pre.

    Args:
        target_folder (str): Folder to scan for json files with prefix.
        prefix (str): Prefix the files' name should start with to be included.

    Returns:
        list[tuple[dict, str]]: List of tuples where each tuple contains
        the json dict and the file name.
    """
    path = os.path.join(os.path.dirname(target_folder), "data")
    obj = os.scandir(path)
    files = []
    for entry in obj:
        if entry.is_file():
            file_arr = entry.name.split(".")
            file_name = file_arr[0]
            file_type = file_arr[-1]
            if entry.name.startswith(prefix) and file_type.lower() == "json":
                file_path = os.path.join(target_folder, entry.name)
                files.append((load_json_from_file(file_path), file_name))

    return files
