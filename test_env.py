from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Print environment variables (without showing full token)
github_token = os.environ.get("GITHUB_TOKEN", "")
token_preview = github_token[:5] + "..." if github_token else "Not found"

print("Environment Variables Check:")
print(f"GitHub User: {os.environ.get('GITHUB_USER', 'Not found')}")
print(f"GitHub Repo: {os.environ.get('GITHUB_REPO', 'Not found')}")
print(f"GitHub Token: {token_preview}")
print(f"GCP Project: {os.environ.get('GOOGLE_CLOUD_PROJECT', 'Not found')}")
print(f"GCP Credentials: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'Not found')}")
print(f"Flask Environment: {os.environ.get('FLASK_ENV', 'Not found')}")
