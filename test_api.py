import os
import time
import requests

def test_gemini_connection():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is missing.")
        return

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key.strip()
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": "Say hello and confirm you are online in 5 words or less."}]
        }]
    }

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Connecting to Gemini (Attempt {attempt}/{max_retries})...")
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            # If we hit a 503, raise it so the except block catches it
            if response.status_code == 503:
                print("Server is busy (503). Retrying shortly...")
                time.sleep(3)
                continue
                
            response.raise_for_status()
            data = response.json()
            
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"API Success! Response: {reply.strip()}")
            return
            
        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error occurred: {err}")
            print(f"Server Response Details: {response.text}")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    print("Failed to connect after multiple attempts. Try running the script again in a minute.")

if __name__ == "__main__":
    test_gemini_connection()