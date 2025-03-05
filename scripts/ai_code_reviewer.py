from operator import contains
from queue import Empty
from tokenize import Number
from turtle import position
from urllib import response
import openai
from openai import AzureOpenAI
import requests
import json
from langchain.schema import HumanMessage
import os
import re
from github import Github

# Set your workspace id
workspace_id = "AIspacelaBi"  # Open workspace console to get your workspace_id

# Set your model name, for available model names please refer documentation
model_name = "gpt-4-turbo"

# Create a dictionary payload with workspace_id and model_name
payload = {
    "workspace_id": workspace_id,
    "model_name":model_name,
    "oai_access":"apim"
}
# Define the URL for the request
url = "https://aiplatform.gcs.int.thomsonreuters.com/v1/openai/token"

# Send a POST request to the URL with headers and the payload
resp = requests.post(url,headers=None, json=payload)

# Load the response content as JSON
credentials = json.loads(resp.content)
# Check if the credentials contain a token and openai_endpoints
if "openai_key" in credentials :
    success_flag = 1
else:
    success_flag = 0
    print("Incorrect Workspace ID or Model Name")

if success_flag == 1:
    # Assign the OpenAI URL and Key from the credentials
    OPENAI_BASE_URL = credentials["openai_endpoint"]
    OPENAI_API_KEY = credentials["openai_key"]

    # If the credentials were successful, print the OpenAI URL and Key
    print(f"OpenAI URL - {OPENAI_BASE_URL}, and OpenAI Key - {OPENAI_API_KEY}\n\n")

# Ensure you have set your API key in your environment variables
api_key = os.getenv(OPENAI_API_KEY)
openai.api_key = api_key
g = Github("GITHUB_TOKEN")
# Replace 'your_username/your_repo' with the specific repo you want to analyze
repo = g.get_repo("Code review with AI")

print("Repo Name" + repo.name)  # Repository name
pr = repo.get_pull()

# Function to analyze code and return feedback
def analyze_code(file_content):   
    api_version = '2024-02-01' # this might change in the future

    client = AzureOpenAI(
        api_key=OPENAI_API_KEY,  
        api_version=api_version,
        base_url=f"{OPENAI_BASE_URL}/openai/deployments/{model_name}"
    )
    print("Reviewing code by AI, Please wait....")
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            #{ "role": "assistant", "content": file_content},
            #{ "role" : "user", "content" : file_content},
            { "role": "assistant", "content": [  
                { 
                    "type": "text", 
                    "text": "Give comments for issues with actual line number in the file_content:" + file_content
                }
            ] } 
        ],
        max_tokens=2000
    )
    return response

for file in pr.get_files():
        resonse = analyze_code(file.patch)
        if resonse:
            comment_body = resonse.choices[0].message.content
            print(comment_body)
            comment_body = comment_body.splitlines()
            
        for commit_id in pr.get_commits():
            varrr = commit_id
            for line_content in comment_body:
                if(len(line_content) > 0):
                    if "Line " in line_content or "Lines " in line_content or "line " in line_content or "lines " in line_content:
                        line_position = int((re.findall(r'\d+', line_content))[1])
                        if "Lines " in line_content or "lines " in line_content:
                            line_position = int((re.findall(r'\d+', line_content))[2])
                        pr.create_review_comment(
                            body = line_content,
                            commit = varrr,
                            path = file.filename, 
                            line = line_position,
                            side = "LEFT"
                            )
                        print(f"Commented on PR #{pr.number}: {comment_body}")
                        pr.create_issue_comment("Reviewed code and added some comments, please have a look and resolve")
                        print(f"Commented on PR #{pr.number}: {comment_body}")

print("Code review by AI has been completed, please check PR for details...")
