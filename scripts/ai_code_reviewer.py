import os
import requests
import json
import re

# Set your environment variables
WORKFLOW_ID = os.getenv("WORKFLOW_ID")

# Set up GitHub access
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
repo = os.getenv("Code-review-with-AI")
pr = os.getenv("PULL_REQUEST_NUMBER")
oa_token = os.getenv("OPEN_ARENA_TOKEN")

# Function to analyze code and return feedback using Open Arena API
def analyze_code(file_content):
    headers = {
        "Authorization": f"Bearer {oa_token}",
        "Content-Type": "application/json"
    }
    data = {
        "workflow_id": WORKFLOW_ID,
        "query": file_content,
        "is_persistence_allowed": False,
        "modelparams": {
            "openai_gpt-4-turbo": {
                "system_prompt": "You are an experienced code reviewer. Provide feedback on the code changes.",
                "temperature": 0.5,
                "max_tokens": 800
            }
        }
    }
    try:
        response = requests.post("https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference", headers=headers, json=data)
        response.raise_for_status()
        return response.json().get('answer', '').strip()
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None

for file in pr.get_files():
    response = analyze_code(file.patch)
    if response:
        comment_body = response.splitlines()

        for commit in pr.get_commits():
            for line_content in comment_body:
                if line_content:
                    match = re.search(r'(?i)lines? (\d+)', line_content)
                    if match:
                        line_position = int(match.group(1))
                        try:
                            pr.create_review_comment(
                                body=line_content,
                                commit=commit,
                                path=file.filename,
                                line=line_position,
                                side="LEFT"
                            )
                            print(f"Commented on PR #{pr.number}: {line_content}")
                        except Exception as e:
                            print(f"Failed to comment on PR: {e}")

        try:
            pr.create_issue_comment("Reviewed code and added some comments, please have a look and resolve")
            print(f"Added general comment to PR #{pr.number}")
        except Exception as e:
            print(f"Failed to add general comment to PR: {e}")

print("Code review by AI has been completed, please check PR for details...")
