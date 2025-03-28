import os
import re


def clean_txt_files(input_folder, recursive=False):
    """Cleans the content of text files by replacing triple or more new lines
    with double new lines and removes Line Separator (LS) and Paragraph
    Separator (PS) in all .txt files in the specified directory."""

    # Iterate over all files in the input directory
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if not filename.endswith(".txt"):
                continue

            # Construct full file path
            file_path = os.path.join(root, filename)

            # Read the content of the .txt file
            with open(file_path, "r", encoding="utf-8") as txt_file:
                content = txt_file.read()

            # Replace triple or more new lines with double new lines
            # Consider lines with only a space as empty lines
            content = re.sub(r"(?:\n[ \t]*){3,}", "\n\n", content)

            # Remove Line Separator (LS) and Paragraph Separator (PS)
            content = content.replace("\u2028", "").replace("\u2029", "")

            # Write the modified content back to the .txt file
            with open(file_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(content)

            print(f"Processed {filename} in {file_path}")

        if not recursive:
            break


input_folder = input("Path to the folder containing .txt files: ").strip()
recursive = (
    input("Do you want to process all .txt files in subdirectories? (y/n): ")
    .strip()
    .lower()
    == "y"
)

clean_txt_files(input_folder, recursive)
