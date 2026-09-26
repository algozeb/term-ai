import os
import json
import time
import requests
from test_context import get_context

def generate_command(user_prompt, context):
    """Sends prompt + system context to Gemini and returns a parsed dictionary safely with 503 retry logic."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is missing.")
        return None

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key.strip()
    }
    
    system_instruction = f"""
    You are an autonomous CLI assistant.
    Target System: {context['os']} ({context['os_release']})
    Shell: {context['shell']}
    Directory: {context['cwd']}
    Local Files Snapshot: {context['directory_listing']}

    Convert the user request into a terminal command matching this exact JSON schema:
    {{
      "command": "the exact shell command to run",
      "summary": "a brief 1-sentence explanation",
      "destructive": true or false,
      "notes": "any relevant caveats or empty string"
    }}
    """

    payload = {
        "contents": [{
            "parts": [{"text": f"{system_instruction}\nUser Request: {user_prompt}"}]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            # Handle transient 503 server overload errors gracefully
            if response.status_code == 503:
                print(f"Server busy (503) on attempt {attempt}/{max_retries}. Retrying in 3 seconds...")
                time.sleep(3)
                continue
                
            response.raise_for_status()
            
            data = response.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            parsed_data = json.loads(raw_text)
            
            required_keys = ["command", "summary", "destructive", "notes"]
            for key in required_keys:
                if key not in parsed_data:
                    raise ValueError(f"Missing required JSON key: {key}")
                    
            return parsed_data

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err} - Details: {response.text}")
            break
        except json.JSONDecodeError:
            print("Error: Model returned invalid JSON format. Raw output was:")
            print(raw_text)
            break
        except Exception as e:
            print(f"An unexpected error occurred during generation: {e}")
            break
        
    return None

if __name__ == "__main__":
    ctx = get_context()
    prompt = "show all files in this directory"
    print(f"Sending prompt: '{prompt}'...")
    
    result = generate_command(prompt, ctx)
    if result:
        print("\nSuccessfully Parsed JSON Result:")
        for k, v in result.items():
            print(f"  {k}: {v}")