"""
Converts .msg files to .txt files in bulk using Python.
Requirements:
extract-msg==0.54.0
"""

import os
import extract_msg


def msg_to_txt(input_folder, output_folder, recursive=False):
    """Converts .msg files to .txt files in bulk."""

    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all files in the input directory
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if not filename.endswith(".msg"):
                continue

            # Construct full file path
            file_path = os.path.join(root, filename)

            # Extract the content of the .msg file
            msg = extract_msg.Message(file_path)
            msg_text = msg.body

            # Define the output file path
            if recursive:
                relative_path = os.path.relpath(root, input_folder)
                output_dir_path = os.path.join(output_folder, relative_path)
                output_file_path = os.path.join(
                    output_dir_path, filename.replace(".msg", ".txt")
                )

                os.makedirs(output_dir_path, exist_ok=True)

            else:
                output_file_path = os.path.join(
                    output_folder, filename.replace(".msg", ".txt")
                )

            # Write the content to a .txt file
            with open(output_file_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(msg_text)

            print(f"Converted {filename} to {output_file_path}")


input_folder = input("Path to the folder containing .msg files: ").strip()
output_folder = input("Path to the output folder for .txt files: ").strip()
recursive = (
    input("Do you want to convert all .msg files in subdirectories? (y/n): ")
    .strip()
    .lower()
    == "y"
)

msg_to_txt(input_folder, output_folder, recursive)
