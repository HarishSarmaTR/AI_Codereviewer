
import os
import requests
import re

def review_code(diff, open_arena_token):
    """Sends the diff to the OpenAI API for review and retrieves comments."""
    headers = {'Authorization': f'Bearer {open_arena_token}', 'Content-Type': 'application/json'}
    data = {
        "workflow_id": "80f448d2-fd59-440f-ba24-ebc3014e1fdf",
        "query": "hi",
        "is_persistence_allowed": "false",
        "modelparams": {
            "openai_gpt-4-turbo": {
                "temperature": "0.7",
                "top_p": "0.9",
                "frequency_penalty": "0",
                "system_prompt": "You are a helpful, respectful and honest assistant.",
                "max_tokens": "800",
                "presence_penalty": "0"
            }
        }
    }

    try:
        response = requests.post("https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference", headers=headers, json=data)
        print("Response Headers:", response.headers)

        if response.status_code == 200:
            ai_response = response.json()
            print(f"OpenAI API Usage: {ai_response}")
        else:
            raise Exception(f"OpenAI Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Failed to review code: {e}")
        return ""
    
if __name__ == "__main__":
    token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJERTBPVEF3UVVVMk16Z3hPRUpGTkVSRk5qUkRNakkzUVVFek1qZEZOVEJCUkRVMlJrTTRSZyJ9.eyJodHRwczovL3RyLmNvbS9mZWRlcmF0ZWRfdXNlcl9pZCI6IjYxMTQxNzkiLCJodHRwczovL3RyLmNvbS9mZWRlcmF0ZWRfcHJvdmlkZXJfaWQiOiJUUlNTTyIsImh0dHBzOi8vdHIuY29tL2xpbmtlZF9kYXRhIjpbeyJzdWIiOiJvaWRjfHNzby1hdXRofFRSU1NPfDYxMTQxNzkifV0sImh0dHBzOi8vdHIuY29tL2V1aWQiOiIxYTBmNTU2Yy0xYWE4LTQ3MmUtYmQwNi02MDY1MjNkYmRkYTAiLCJodHRwczovL3RyLmNvbS9hc3NldElEIjoiYTIwODE5OSIsImlzcyI6Imh0dHBzOi8vYXV0aC50aG9tc29ucmV1dGVycy5jb20vIiwic3ViIjoiYXV0aDB8NjM3Y2M1YmRhZTNkYjM1MjEzYjEyY2VlIiwiYXVkIjpbIjQ5ZDcwYTU4LTk1MDktNDhhMi1hZTEyLTRmNmUwMGNlYjI3MCIsImh0dHBzOi8vbWFpbi5jaWFtLnRob21zb25yZXV0ZXJzLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE3NDEwODM5NDMsImV4cCI6MTc0MTE3MDM0Mywic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImF6cCI6InRnVVZad1hBcVpXV0J5dXM5UVNQaTF5TnlvTjJsZmxJIn0.aH1pPN7MNcmH-fqkxPbncTipGKY6_kSY-iC9HA-5DNnq14o9Ir8_Duk8HghuVaDz-llRQK6sFQxyXA1Lk4W80kShQF5fybuj9eMpOn_W2ZNCrpd3OuFhIR77IwegeNK5IHnlMzrWAUbwVAJ65P3EHIZEL1MRycoQgipVbbFIJBKXRhttklvfwvGEWgWa_mu-bdVSmgdY0eiPw67TeRdCnnZ1OQo7H9LhhbBag8adC9GYQoTlKSkG-N0g6zt5qVdDZ_iFysM1OTF0NpD6RRYuzh6RCazMTCpomObquKJF0gkpr1CLIf-thXyfg88DbWpyYhdkEcQoHuBmL-YINT4l6g'
    review_code("",token)
