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
    """Mendapatkan informasi email dari kredensial."""
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
            print("❌ Tidak dapat menemukan alamat email.")
            return "unknown_email"
    except Exception as e:
        print(f"❌ Error saat mengambil info akun: {e}")
        return "unknown_email"


def get_service(credential_path, port=8080):
    """Mendapatkan service API YouTube dan email akun."""
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
                print(f"⚠️ Gagal merefresh token untuk {credential_path}: {e}")
                # Hapus token yang rusak agar bisa dibuat ulang
                os.remove(TOKEN_FILE)
                return None, None
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
                creds = flow.run_local_server(port=port)
            except Exception as e:
                print(f"❌ Gagal membuat token baru untuk {credential_path}: {e}")
                return None, None

        os.makedirs(credential_path, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    # Dapatkan dan simpan email jika belum ada
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
    """Memastikan semua akun memiliki token yang valid sebelum memulai."""
    print("🔑 Memeriksa semua token akun YouTube...")
    for i in range(1, YT_ACC + 1):
        credential_path = os.path.join("yt_credential", f"acc{i}")
        os.makedirs(credential_path, exist_ok=True)
        print(f"   -> Memeriksa {credential_path}...")
        get_service(credential_path, port=8080 + i)
        print_account_info(credential_path)

def print_account_info(credential_path):
    """Mencetak informasi email yang tersimpan."""
    try:
        files = os.listdir(credential_path)
        email_files = [f for f in files if f != 'token.json']
        if email_files:
            print(f"   ✅ Email Ditemukan: {email_files[0]}")
        else:
            print(f"   ⚠️ Email tidak ditemukan di {credential_path}.")
    except FileNotFoundError:
        print(f"   ⚠️ Direktori kredensial tidak ditemukan: {credential_path}")

def upload_to_youtube(credential_path, file, title, desc, privacy="public", category="22"):
    """Fungsi untuk mengunggah satu video ke satu channel YouTube."""
    youtube, email = get_service(credential_path)
    if not youtube:
        print(f"❌ Gagal mendapatkan layanan YouTube untuk {credential_path}. Akun ini dilewati.")
        return None

    body = {
        "snippet": {"title": title, "description": desc, "categoryId": category},
        "status": {"privacyStatus": privacy},
    }
    
    print(f"📹 Memulai unggah ke channel '{email}' ({credential_path})...")
    try:
        media = MediaFileUpload(file, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   Proses unggah ({email}): {int(status.progress() * 100)}%")
        
        print(f"✅ Berhasil diunggah ke '{email}'! ID Video: {response['id']}")
        return response['id']
    except Exception as e:
        print(f"❌ Gagal mengunggah ke '{email}' ({credential_path}): {e}")
        # Jangan `raise` error, cukup kembalikan None agar proses lanjut
        return None

async def upload_task(executor, credential_path, video_path, title, description):
    """Tugas asinkron untuk menjalankan fungsi upload di thread terpisah."""
    loop = asyncio.get_event_loop()
    try:
        # Menjalankan fungsi upload_to_youtube yang bersifat blocking di dalam executor
        await loop.run_in_executor(executor, upload_to_youtube, credential_path, video_path, title, description)
    except Exception as e:
        # Tangani error tak terduga di level ini sebagai fallback
        # Ini seharusnya tidak sering terjadi karena error sudah ditangani di dalam upload_to_youtube
        print(f"❌ Terjadi error tak terduga pada tugas untuk {credential_path}: {e}")

async def upload_to_all_channels_async(video_path, title, description):
    """Mengelola semua tugas unggah secara asinkron."""
    tasks = []
    # ThreadPoolExecutor digunakan karena library Google API tidak native asyncio
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for i in range(1, YT_ACC + 1):
            credential_path = os.path.join("yt_credential", f"acc{i}")
            # Membuat tugas untuk setiap akun
            task = upload_task(executor, credential_path, video_path, title, description)
            tasks.append(task)
        
        # Menunggu semua tugas selesai
        await asyncio.gather(*tasks)

def start_async_upload(video_path, title, description):
    """Fungsi utama untuk memulai proses unggah ke semua channel."""
    # 1. Pastikan semua token siap sebelum mulai mengunggah
    ensure_all_tokens()
    
    # 2. Jalankan proses unggah secara asinkron
    print("\n🚀 Memulai proses unggah ke semua channel YouTube...")
    asyncio.run(upload_to_all_channels_async(video_path, title, description))
    print("\n✨ Semua proses unggah YouTube telah selesai.")

if __name__ == '__main__':
    # Contoh cara menjalankan skrip ini
    # Pastikan file video dan data lainnya sudah ada
    video_file = "path/to/your/video.mp4"
    video_title = "Judul Video Keren"
    video_description = "Ini adalah deskripsi video yang sangat menarik."

    if os.path.exists(video_file):
        start_async_upload(video_file, video_title, video_description)
    else:
        print(f"File video tidak ditemukan di '{video_file}'. Harap ganti path di dalam blok if __name__ == '__main__'.")

