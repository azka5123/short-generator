import asyncio
from concurrent.futures import ThreadPoolExecutor
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import os
import shutil

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/userinfo.profile",
]
YT_ACC = int(os.getenv("YT_ACC", 1))
MAX_WORKERS = int(os.getenv("YT_WORKER", 1))

def get_account_info(creds):
    service = build('people', 'v1', credentials=creds)
    try:
        profile = service.people().get(
            resourceName='people/me',
            personFields='emailAddresses'
        ).execute()
        emails = profile.get('emailAddresses', [])
        if emails:
            return emails[0].get('value')
        else:
            raise ValueError("❌ Email address not found in People API response")
    except Exception as e:
        print(f"❌ Error getting account info: {e}")
        return "unknown_email"


def get_service(credential_path, port = 8080):
    CLIENT_SECRETS = os.path.join("yt_credential", "client_secret.json")
    TOKEN_FILE = os.path.join(credential_path, "token.json")

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh()
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=port)
        os.makedirs(credential_path, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    email = get_account_info(creds)

    # make empty file for email
    email_file_path = os.path.join(credential_path, email)
    if not os.path.exists(email_file_path):
        open(email_file_path, 'w').close() 

    return build("youtube", "v3", credentials=creds), email

def ensure_all_tokens():
    # generate all token
    for i in range(1, YT_ACC + 1):
        credential_path = os.path.join("yt_credential", f"acc{i}")
        os.makedirs(credential_path, exist_ok=True)
        print(f"🔑 Check Token For {credential_path} ...")
        get_service(credential_path, port = 8080 + i)
        print_account_info(credential_path)

def print_account_info(credential_path):
    files = os.listdir(credential_path)
    email_files = [f for f in files if f != 'token.json']

    if email_files:
        print(f"📧 Got Email In {credential_path}: {email_files[0]}")
    else:
        print(f"⚠️ Email Didnt Found In {credential_path}.")
        
def upload_to_youtube(credential_path, file, title, desc, privacy="public", category="22"):
    youtube,email = get_service(credential_path)
    body = {
        "snippet": {"title": title, "description": desc, "categoryId": category},
        "status": {"privacyStatus": privacy},
    }
    media = MediaFileUpload(file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    print(f"📹 Starting Upload To Youtube Channel (Credential: {credential_path})...")
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload Progress ({credential_path}): {int(status.progress() * 100)}%")
    print(f"✅ Upload Success {credential_path}! Video ID: {response['id']}")

async def upload_task(executor, credential_path, video_path, title, description):
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(executor, upload_to_youtube, credential_path, video_path, title, description)
    except Exception as e:
        print(f"❌ Error upload {credential_path}: {e}")

async def upload_to_all_channels_async(video_path, title, description):
    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for i in range(1, YT_ACC + 1):
            credential_path = os.path.join("yt_credential", f"acc{i}")
            task = upload_task(executor, credential_path, video_path, title, description)
            tasks.append(task)
        await asyncio.gather(*tasks)

def start_async_upload(video_path, title, description):
    ensure_all_tokens()
    asyncio.run(upload_to_all_channels_async(video_path, title, description))
