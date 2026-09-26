import os
import platform

def get_context():
    """Gathers OS, release, shell, cwd, and a safe short directory listing."""
    
    # Safely list the first few files in the current directory (cross-platform)
    try:
        items = os.listdir(os.getcwd())
        # Limit to 10 items to keep prompt payloads lightweight and clean
        dir_listing = ", ".join(items[:10])
        if len(items) > 10:
            dir_listing += " (and more...)"
    except Exception as e:
        dir_listing = f"Error reading directory: {e}"

    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "shell": os.environ.get("SHELL", os.environ.get("ComSpec", "unknown")),
        "cwd": os.getcwd(),
        "directory_listing": dir_listing
    }

if __name__ == "__main__":
    ctx = get_context()
    print("--- Enhanced System Context ---")
    for key, value in ctx.items():
        print(f"{key.upper()}: {value}")