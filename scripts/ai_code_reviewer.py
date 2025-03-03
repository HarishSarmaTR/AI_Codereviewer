import os
import requests
import json
from github import Github
import re

# Set your environment variables
WORKFLOW_ID = os.getenv("WORKFLOW_ID")

# Set up GitHub access
g = Github(os.getenv("GITHUB_TOKEN"))
repo = g.get_repo("REPOSITORY_NAME")
pr = repo.get_pull(PULL_REQUEST_NUMBER)

# Function to analyze code and return feedback using Open Arena API
def analyze_code(file_content):
    headers = {
        "Authorization": f"Bearer {OPEN_ARENA_TOKEN}",
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
    response = requests.post("https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference", headers=headers, json=data)
    response.raise_for_status()
    return response.json()['answer'].strip()

for file in pr.get_files():
    response = analyze_code(file.patch)
    if response:
        comment_body = response
        print(comment_body)
        comment_body = comment_body.splitlines()

    for commit_id in pr.get_commits():
        varrr = commit_id
        for line_content in comment_body:
            if len(line_content) > 0:
                if "Line " in line_content or "Lines " in line_content or "line " in line_content or "lines " in line_content:
                    line_position = int((re.findall(r'\d+', line_content))[1])
                    if "Lines " in line_content or "lines " in line_content:
                        line_position = int((re.findall(r'\d+', line_content))[2])
                    pr.create_review_comment(
                        body=line_content,
                        commit=varrr,
                        path=file.filename,
                        line=line_position,
                        side="LEFT"
                    )
                    print(f"Commented on PR #{pr.number}: {comment_body}")
                    pr.create_issue_comment("Reviewed code and added some comments, please have a look and resolve")
                    print(f"Commented on PR #{pr.number}: {comment_body}")

print("Code review by AI has been completed, please check PR for details...")
