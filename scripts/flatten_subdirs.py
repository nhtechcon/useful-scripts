"""
Example:
- in: my/long/file/dir/data.zip
- out: my_long_file_dir_data.zip
"""

import os


def flatten_directory_structure(input_folder, output_folder):
    """Flattens directory structure into filenames with underscores."""

    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all files in the input directory
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            # Construct full file path
            file_path = os.path.join(root, filename)

            # Construct the new filename by concatenating directory names with underscores
            relative_path = os.path.relpath(root, input_folder)
            dir_names = os.path.normpath(relative_path).split(os.sep)
            new_filename = "_".join(dir_names + [filename])

            # Define the output file path
            output_file_path = os.path.join(output_folder, new_filename)

            # Copy the content to the new file path
            with open(file_path, "rb") as src_file, open(
                output_file_path, "wb"
            ) as dest_file:
                dest_file.write(src_file.read())

            print(f"Flattened {file_path} to {output_file_path}")


input_folder = input("Path to the folder to flatten: ").strip()
output_folder = input("Path to the output folder for flattened files: ").strip()

flatten_directory_structure(input_folder, output_folder)
