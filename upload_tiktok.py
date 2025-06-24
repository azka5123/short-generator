import os
from tiktok_uploader.upload import upload_video

def upload_tiktok(video_path: str, description: str, cookies_dir: str = 'tiktok_cookies'):
    """
    Uploads the video to all TikTok accounts based on all cookies.txt files in the specified folder.

    :param video_path: Path to the video file (MP4)
    :param description: TikTok video description
    :param cookies_dir: Directory containing all TikTok account cookies files (default: 'tiktok_cookies')
    """

    # Cek apakah folder cookies ada
    if not os.path.isdir(cookies_dir):
        print(f"❌ Folder cookies '{cookies_dir}' tidak ditemukan!")
        return

    # Ambil semua file .txt di dalam folder cookies
    cookie_files = [f for f in os.listdir(cookies_dir) if f.endswith('.txt')]

    if not cookie_files:
        print("❌ Tidak ada file cookie .txt ditemukan di folder cookies!")
        return

    # Upload ke setiap akun (cookie file)
    for cookie_file in cookie_files:
        cookie_path = os.path.join(cookies_dir, cookie_file)
        print(f"\n🚀 Upload pakai cookie: {cookie_path}")
        try:
            upload_video(
                video_path,
                description=description,
                cookies=cookie_path
            )
            print(f"✅ Sukses upload dengan cookie: {cookie_file}\n")
        except Exception as e:
            print(f"❌ Gagal upload pakai {cookie_file}: {e}\n")
