# Logseq Blogpost Uploader

This script streamlines the process of uploading blog posts to a GitHub repository, automating the creation of dedicated folders for each post, organizing assets, and formatting content according to predefined rules. It is tailored to work seamlessly with a Markdown file containing a blog post and its associated assets.

## Prerequisites
Before utilizing this script, ensure the following prerequisites are met:
- Python 3 is installed.
- Required Python packages are installed.

## Configuration
Before executing the script, replace the following placeholders within the script:
- `YOUR_GITHUB_TOKEN`: Your GitHub access token with repository permissions.
- `YOUR_GITHUB_USERNAME`: Your GitHub username.
- `YOUR_GITHUB_REPO`: Your GitHub repository name.
- `YOUR_ASSETS_FOLDER`: The folder where your assets (images) are stored.
- `YOUR_LOCAL_FOLDER`: The local folder where the blog post folders will be created.

## Formatting Checks
The script incorporates various formatting checks to ensure consistency in your Markdown content, including:
- Removal of duplicate metadata
- Fixing image reference indentation
- Adjusting formatting for transformed content
- Changing asset paths from `../assets/` to `/media/`
- Cleaning up unnecessary characters and formatting

## Folder Structure
The script generates a dedicated folder for each blog post within the specified local folder. The folder structure comprises:
- `index.md`: The formatted blog post content.
- `media/`: A subfolder containing associated media files (images).

## Note
The script is designed for a specific Markdown structure (Logseq structure) and may need adjustments for different setups, such as using Obsidian. Ensure your GitHub token has the necessary permissions to create and update repository contents.
