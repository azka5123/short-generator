import asyncio
from concurrent.futures import ThreadPoolExecutor
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
import shutil

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]
YT_ACC = int(os.getenv("YT_ACC", 1))
MAX_WORKERS = int(os.getenv("YT_WORKER", 1))

def get_account_info(creds):
    """Gets email information from credentials."""
    try:
        service = build('people', 'v1', credentials=creds)
        profile = service.people().get(
            resourceName='people/me',
            personFields='emailAddresses'
        ).execute()
        emails = profile.get('emailAddresses', [])
        if emails:
            return emails[0].get('value')
        else:
            print("❌ Could not find email address.")
            return "unknown_email"
    except Exception as e:
        print(f"❌ Error getting account info: {e}")
        return "unknown_email"


def get_service(credential_path, port=8080):
    """Gets the YouTube API service and account email."""
    CLIENT_SECRETS = os.path.join("yt_credential", "client_secret.json")
    TOKEN_FILE = os.path.join(credential_path, "token.json")

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️ Failed to refresh token for {credential_path}: {e}")
                # Delete the corrupted token so it can be recreated
                os.remove(TOKEN_FILE)
                return None, None
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
                creds = flow.run_local_server(port=port)
            except Exception as e:
                print(f"❌ Failed to create new token for {credential_path}: {e}")
                return None, None

        os.makedirs(credential_path, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    # Get and save the email if it doesn't exist
    email_files = [f for f in os.listdir(credential_path) if "@" in f]
    if email_files:
        email = email_files[0]
    else:
        email = get_account_info(creds)
        email_file_path = os.path.join(credential_path, email)
        if not os.path.exists(email_file_path):
            open(email_file_path, 'w').close()

    return build("youtube", "v3", credentials=creds), email

def ensure_all_tokens():
    """Ensures all accounts have valid tokens before starting."""
    print("🔑 Checking all YouTube account tokens...")
    for i in range(1, YT_ACC + 1):
        credential_path = os.path.join("yt_credential", f"acc{i}")
        os.makedirs(credential_path, exist_ok=True)
        print(f"   -> Checking {credential_path}...")
        get_service(credential_path, port=8080 + i)
        print_account_info(credential_path)

def print_account_info(credential_path):
    """Prints the stored email information."""
    try:
        files = os.listdir(credential_path)
        email_files = [f for f in files if f != 'token.json']
        if email_files:
            print(f"   ✅ Email Found: {email_files[0]}")
        else:
            print(f"   ⚠️ Email not found in {credential_path}.")
    except FileNotFoundError:
        print(f"   ⚠️ Credential directory not found: {credential_path}")

def upload_to_youtube(credential_path, file, title, desc, privacy="public", category="22"):
    """Function to upload one video to one YouTube channel."""
    youtube, email = get_service(credential_path)
    if not youtube:
        print(f"❌ Failed to get YouTube service for {credential_path}. Skipping this account.")
        return None

    body = {
        "snippet": {"title": title, "description": desc, "categoryId": category},
        "status": {"privacyStatus": privacy},
    }
    
    print(f"📹 Starting upload to channel '{email}' ({credential_path})...")
    try:
        media = MediaFileUpload(file, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   Upload process ({email}): {int(status.progress() * 100)}%")
        
        print(f"✅ Successfully uploaded to '{email}'! Video ID: {response['id']}")
        return response['id']
    except Exception as e:
        print(f"❌ Failed to upload to '{email}' ({credential_path}): {e}")
        # Don't `raise` an error, just return None so the process can continue
        return None

async def upload_task(executor, credential_path, video_path, title, description):
    """Asynchronous task to run the upload function in a separate thread."""
    loop = asyncio.get_event_loop()
    try:
        # Run the blocking upload_to_youtube function in the executor
        await loop.run_in_executor(executor, upload_to_youtube, credential_path, video_path, title, description)
    except Exception as e:
        # Handle unexpected errors at this level as a fallback
        # This shouldn't happen often as errors are handled within upload_to_youtube
        print(f"❌ An unexpected error occurred in the task for {credential_path}: {e}")

async def upload_to_all_channels_async(video_path, title, description):
    """Manages all upload tasks asynchronously."""
    tasks = []
    # ThreadPoolExecutor is used because the Google API library is not native asyncio
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for i in range(1, YT_ACC + 1):
            credential_path = os.path.join("yt_credential", f"acc{i}")
            # Create a task for each account
            task = upload_task(executor, credential_path, video_path, title, description)
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

def start_async_upload(video_path, title, description):
    """Main function to start the upload process to all channels."""
    # 1. Make sure all tokens are ready before starting the upload
    ensure_all_tokens()
    
    # 2. Run the upload process asynchronously
    print("\n🚀 Starting upload process to all YouTube channels...")
    asyncio.run(upload_to_all_channels_async(video_path, title, description))
    print("\n✨ All YouTube upload processes have been completed.")

if __name__ == '__main__':
    # Example of how to run this script
    # Make sure the video file and other data exist
    video_file = "path/to/your/video.mp4"
    video_title = "Cool Video Title"
    video_description = "This is a very interesting video description."

    if os.path.exists(video_file):
        start_async_upload(video_file, video_title, video_description)
    else:
        print(f"Video file not found at '{video_file}'. Please change the path in the if __name__ == '__main__' block.")

