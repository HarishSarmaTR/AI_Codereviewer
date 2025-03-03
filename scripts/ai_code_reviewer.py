import os
import requests
import json
import time

def fetch_diff(pr_url, github_token):
    """Fetches the diff of the pull request from GitHub."""
    headers = {'Authorization': f'token {github_token}', 'Accept': 'application/vnd.github.v3+json'}
    try:
        response = requests.get(f"{pr_url}/files", headers=headers)
        response.raise_for_status()
        files = response.json()
        diff = ''.join(file.get('patch', '') for file in files)
        return diff
    except requests.RequestException as e:
        raise Exception(f"Error fetching PR diff: {e}")

def review_code(diff, open_arena_token, workflow_id, retries=3, delay=10):
    """Sends the diff to the Open Arena API for review and retrieves comments."""
    headerss = {'Authorization': f'Bearer {open_arena_token}', 'Content-Type': 'application/json'}
    data = {
        "workflow_id": "8556ba87-acf8-4049-98a3-fc62a300656c",
        "query": diff,
        "is_persistence_allowed": False,
        "modelparams": {
            "openai_gpt-4o": {
                "system_prompt": "You are an experienced code reviewer. Provide feedback on the code changes.",
                "temperature": 0.5,
                "max_tokens": 14000
            }
        }
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post("https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference", headers=headerss, json=data)

            if response.status_code == 200:
                ai_response = response.json()
                return ai_response['answer'].strip()
            else:
                raise Exception(f"Open Arena Error: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                print(f"Retrying in {delay}s...")
                time.sleep(delay)

    # Fallback response when API fails after retries
    return (
        "AI review unavailable at the moment. Here are some general suggestions:\n\n"
        "1. Ensure proper error handling is in place for edge cases.\n"
        "2. Refactor complex functions into smaller, reusable methods.\n"
        "3. Add comments where the logic might be unclear to others.\n"
        "4. Check for any potential memory leaks or performance issues.\n"
        "5. Follow coding standards and naming conventions for consistency."
    )

def post_comment(pr_url, comment, token_github):
    """Posts a comment to the pull request on GitHub."""
    try:
        repo = os.getenv('GITHUB_REPOSITORY')
        issue_number = pr_url.split('/')[-1]
        comments_url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
        headers = {'Authorization': f'token {token_github}', 'Content-Type': 'application/json'}
        response = requests.post(comments_url, headers=headers, json={"body": comment})
        response.raise_for_status()
        print("Comment posted successfully.")
    except requests.RequestException as e:
        raise Exception(f"Error posting comment: {e}")

def validate_environment_variables(*vars):
    """Validates the presence of required environment variables."""
    missing_vars = [var for var in vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

def main():
    """Main function to fetch PR diff, review code, and post comments."""
    try:
        validate_environment_variables("GITHUB_PR_URL", "token_github", "OPEN_ARENA_TOKEN", "WORKFLOW_ID")
        pr_url = os.getenv("GITHUB_PR_URL")
        token_github = os.getenv("token_github")
        open_arena_token = os.getenv("OPEN_ARENA_TOKEN")
        workflow_id = os.getenv("WORKFLOW_ID")

        print(f"PR URL: {pr_url}")
        print(f"GitHub Token: {'Provided' if token_github else 'Missing'}")
        print(f"Open Arena Token: {'Provided' if open_arena_token else 'Missing'}")
        print(f"Workflow ID: {workflow_id}")

        # Fetch PR diff
        print("Fetching PR diff...")
        diff = fetch_diff(pr_url, token_github)

        # Review code
        print("Sending diff to Open Arena for review...")
        ai_review = review_code(diff, open_arena_token, workflow_id)
        if not ai_review:
            ai_review = "No significant suggestions provided."

        # Post review comment
        print("Posting review comment...")
        post_comment(pr_url, ai_review, token_github)

        print("AI review process completed successfully.")

    except EnvironmentError as env_err:
        print(f"Environment Error: {env_err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
