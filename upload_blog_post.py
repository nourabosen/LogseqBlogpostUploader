# Replace the following placeholders with your actual values:
# - YOUR_GITHUB_TOKEN
# - YOUR_GITHUB_USERNAME
# - YOUR_GITHUB_REPO
# - YOUR_ASSETS_FOLDER
# - YOUR_LOCAL_FOLDER

import os
import requests
from datetime import datetime
import re
import base64
import argparse
import shutil

# Define the argparse parser and parse the command-line arguments
parser = argparse.ArgumentParser(description="Upload a blog post to GitHub.")
parser.add_argument("markdown_file_path", type=str, help="The path to the Markdown file to upload.")
args = parser.parse_args()

# Define your GitHub token, username, and repo here
github_token = "YOUR_GITHUB_TOKEN"
github_username = "YOUR_GITHUB_USERNAME"
github_repo = "YOUR_GITHUB_REPO"

headers = {
    "Authorization": f"Bearer {github_token}",
    "Content-Type": "application/json",
}

# Define the GitHub API URL
github_api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/content/posts"

# Function to remove duplicate metadata
def remove_duplicate_metadata(content):
    metadata_pattern = r"---(.*?)---"
    metadata_matches = re.findall(metadata_pattern, content, re.DOTALL)
    if len(metadata_matches) > 1:
        content = re.sub(metadata_pattern, r"---\1---", content, count=1)
    return content

# Function to fix image reference indentation
def fix_image_reference_indentation(content):
    image_pattern = r"!\[.*?\]\((.*?)\)"
    def replace_callback(match):
        return match.group(0).lstrip()
    return re.sub(image_pattern, replace_callback, content)

# Function to perform formatting checks
def perform_formatting_checks(content):
    """Transforms Markdown content according to specified rules."""
    # Remove everything after the first image tag
    content = re.sub(r"(?s)!\[.*?\]\(.*?\)\n---\n(.*)", r"\1", content)

    # Fix extra hyphens in tags and remove duplicate social image path
    content = re.sub(r"tags:\n- - ", r"tags:\n- ", content)

    # Adjust formatting for the transformed content
    content = re.sub(r"- \!\[(.*?)\]\((.*?)\)\{:height (\d+), :width (\d+)\}", r"![\1](\2){:height \3, :width \4}", content)
    content = re.sub(r"- # (\S+)", r"# \1", content)
    content = re.sub(r"- ## (\S+)", r"## \1", content)

    # Change ../assets/ to /media/
    content = content.replace("../assets/", "/media/")

    # Remove the first '-'
    content = re.sub(r"^\s*-\s*", "", content, count=1)

    # Remove spaces before '---' and add '---' at the end of the metadata block
    content = re.sub(r"\s+---", "\n---", content)

    # Remove hyphens in new lines after '---'
    content = re.sub(r"\n- ", "\n <br/> <br/>", content)

    return content.strip()  # Remove leading/trailing whitespace

# Function to clean and sanitize a string for use as a folder name
def clean_folder_name(name):
    return re.sub(r'[<>:"/\\|?*]', '', name)

# Function to extract metadata from a given Markdown file
def extract_metadata(markdown_content):
    metadata_pattern = r"---(.*?)---"
    metadata_match = re.search(metadata_pattern, markdown_content, re.DOTALL)
    if metadata_match:
        metadata_content = metadata_match.group(1).strip()
        metadata_content_without_hyphens = re.sub(r"^\s*-\s*", "", metadata_content, flags=re.MULTILINE)
        metadata = {}
        for item in metadata_content_without_hyphens.split("\n"):
            if ":" in item:
                key, value = item.split(":", 1)
                metadata[key.strip()] = value.strip()
        return metadata
    else:
        return {}

# Specify the path to your Markdown file
logseq_page_path = args.markdown_file_path

# Set the correct path for the the assets folder
assets_folder = "YOUR_ASSETS_FOLDER"

# Read the content from the file
with open(logseq_page_path, "r", encoding="utf-8") as file:
    page_content = file.read()

# Extract metadata from the page content
metadata = extract_metadata(page_content)

# Remove duplicate metadata
content_without_duplicates = remove_duplicate_metadata(page_content)

# Fix image reference indentation
content_with_fixed_indentation = fix_image_reference_indentation(content_without_duplicates)

# Perform formatting checks
content_with_formatting_checks = perform_formatting_checks(content_with_fixed_indentation)

# Generate folder name with desired format
title = metadata.get("title", "Untitled")
timestamp = datetime.now().strftime("%Y-%d-%m--")
slug = title.replace("-", "").title().replace(" ", "-")  # Apply title case and replace spaces with dashes
temp_folder = f"{timestamp}-{clean_folder_name(slug)}"

temp_folder_path_local = os.path.join(r"YOUR_LOCAL_FOLDER", temp_folder)
temp_folder_path = os.path.join(temp_folder)
temp_media_folder_path = os.path.join(temp_folder_path, "media")

# Create the local folder if it doesn't exist
if not os.path.exists(temp_folder_path_local):
    os.makedirs(temp_folder_path_local)


# Extract the image path from the content
image_match = re.search(r"!\[.*?\]\((.*?)\)", content_with_formatting_checks)
if image_match:
    image_path_relative = image_match.group(1)
    # Extract the image file name
    image_filename = os.path.basename(image_path_relative)

    # Construct the absolute image path in Dropbox assets folder
    absolute_image_path = os.path.join(dropbox_assets_folder, image_filename)

    # Create the media folder in the local path if it doesn't exist
    if not os.path.exists(temp_media_folder_path):
        os.makedirs(temp_media_folder_path)

    # Check if the image file exists before copying
    if os.path.exists(absolute_image_path):
        # Copy the image to the media folder in the local path
        destination_image_path_local = os.path.join(temp_media_folder_path, image_filename)
        shutil.copyfile(absolute_image_path, destination_image_path_local)
    else:
        print(f"Image file not found: {absolute_image_path}")

# Create the local folder if it doesn't exist
if not os.path.exists(temp_folder_path_local):
    os.makedirs(temp_folder_path_local)

# Write to the file
temp_page_filename = os.path.join(temp_folder_path_local, "index.md")
with open(temp_page_filename, "w", encoding="utf-8") as f:
    f.write(content_with_formatting_checks)

# Copy the media folder to the local path
shutil.copytree(temp_media_folder_path, os.path.join(temp_folder_path_local, "media"))


data = {
    "message": "Upload new page",
    "content": base64.b64encode(content_with_formatting_checks.encode("utf-8")).decode("utf-8"),
}

response = requests.put(
    f"{github_api_url}/{clean_folder_name(temp_folder_path)}/index.md",
    headers=headers,
    json=data
)

# Upload media folder to GitHub
media_folder_path = os.path.join(temp_folder_path, "media")
media_files = [os.path.join(media_folder_path, file) for file in os.listdir(media_folder_path)]
for file in media_files:
    with open(file, "rb") as f:
        encoded_content = base64.b64encode(f.read()).decode("utf-8")
    data = {
        "message": "Upload media file",
        "content": encoded_content
    }
    response = requests.put(
        f"{github_api_url}/{clean_folder_name(temp_folder_path)}/media/{os.path.basename(file)}",
        headers=headers,
        json=data
    )
