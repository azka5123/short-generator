import os
from tiktok_uploader.upload import upload_video
import psutil, os, signal, time

def kill_chrome():
    for proc in psutil.process_iter(['pid', 'name']):
        if "chrome" in proc.info['name'].lower() or "chromedriver" in proc.info['name'].lower():
            try:
                os.kill(proc.info['pid'], signal.SIGTERM)
            except Exception:
                pass

def upload_tiktok(video_path: str, description: str, cookies_dir: str = 'tiktok_cookies'):
    """
    Uploads a video to all TikTok accounts based on the cookies.txt files
    found in the specified directory.

    :param video_path: Path to the video file (MP4).
    :param description: Description for the TikTok video.
    :param cookies_dir: Directory containing the TikTok account cookie files (default: 'tiktok_cookies').
    """

    # 1. Verify video path and cookies directory
    if not os.path.exists(video_path):
        print(f"❌ Video file not found at: {video_path}")
        return

    if not os.path.isdir(cookies_dir):
        print(f"❌ Cookies directory not found at: '{cookies_dir}'")
        return

    # 2. Get all .txt files in the cookies folder
    cookie_files = [f for f in os.listdir(cookies_dir) if f.endswith('.txt')]

    if not cookie_files:
        print(f"ℹ️ No cookie files (.txt) found in the '{cookies_dir}' directory.")
        return

    print(f"🚀 Starting upload process for {len(cookie_files)} TikTok account(s)...")

    # 3. Iterate and upload for each cookie file
    for cookie_file in cookie_files:
        cookie_path = os.path.join(cookies_dir, cookie_file)
        print(f"\n---\n🔄 Attempting to upload with account from: {cookie_file}")

        try:
            upload_video(
                filename=video_path,
                description=description,
                cookies=cookie_path,
                headless=False,
            )
            print(f"✅ Successfully uploaded using: {cookie_file}")
        except Exception as e:
            print(f"❌ Failed to upload with {cookie_file}. Reason: {e}")
        
        # Pastikan Chrome/Chromedriver mati sebelum lanjut
        kill_chrome()
        time.sleep(2)  # kasih jeda biar proses bener-bener mati


if __name__ == '__main__':
    # Example of how to run this function
    video_file_path = "path/to/your/video.mp4"
    video_description = "This is my TikTok video description! #fyp #trending"
    
    # Make sure the video file exists before running
    if os.path.exists(video_file_path):
        upload_tiktok(video_path=video_file_path, description=video_description)
    else:
        print(f"Example video file not found. Please change the 'video_file_path' variable in the if __name__ == '__main__' block.")
