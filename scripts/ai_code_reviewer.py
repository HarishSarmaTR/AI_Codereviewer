import os
import requests
import json
import re

# Set your environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("REPOSITORY_NAME")
pr_number = os.getenv("PULL_REQUEST_NUMBER")
WORKFLOW_ID = os.getenv("WORKFLOW_ID")
OA_TOKEN = os.getenv("OPEN_ARENA_TOKEN")

# Function to get files changed in a pull request
def get_pr_files(repo_name, pr_number):
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Mock function to analyze code (replace with actual AI model call)
def analyze_code(file_content):
    # Simulate AI feedback
    return f"Feedback for code:\n{file_content[:100]}..."  # Truncate for example

# Function to post a comment to a pull request
def post_pr_comment(repo_name, pr_number, comment_body):
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": comment_body
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

# Main script to review code changes
try:
    files = get_pr_files(REPOSITORY_NAME, PULL_REQUEST_NUMBER)
    for file in files:
        feedback = analyze_code(file['patch'])
        if feedback:
            post_pr_comment(REPOSITORY_NAME, PULL_REQUEST_NUMBER, f"File: {file['filename']}\n{feedback}")
            print(f"Posted feedback for {file['filename']}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

print("AI Code Review completed.")
