import os
from tiktok_uploader.upload import upload_video

def upload_tiktok(video_path: str, description: str, cookies_dir: str = 'tiktok_cookies'):
    """
    Mengunggah video ke semua akun TikTok berdasarkan file cookies.txt 
    yang ada di dalam folder yang ditentukan.

    :param video_path: Path ke file video (MP4).
    :param description: Deskripsi untuk video TikTok.
    :param cookies_dir: Direktori yang berisi file-file cookies akun TikTok (default: 'tiktok_cookies').
    """

    # 1. Verifikasi path video dan direktori cookies
    if not os.path.exists(video_path):
        print(f"❌ File video tidak ditemukan di: {video_path}")
        return

    if not os.path.isdir(cookies_dir):
        print(f"❌ Direktori cookies tidak ditemukan di: '{cookies_dir}'")
        return

    # 2. Ambil semua file .txt di dalam folder cookies
    cookie_files = [f for f in os.listdir(cookies_dir) if f.endswith('.txt')]

    if not cookie_files:
        print(f"ℹ️ Tidak ada file cookie (.txt) yang ditemukan di direktori '{cookies_dir}'.")
        return

    print(f"🚀 Memulai proses unggah ke {len(cookie_files)} akun TikTok...")

    # 3. Iterasi dan unggah untuk setiap file cookie
    for cookie_file in cookie_files:
        cookie_path = os.path.join(cookies_dir, cookie_file)
        print(f"\n---\n🔄 Mencoba mengunggah dengan akun dari: {cookie_file}")
        
        try:
            # Panggil fungsi upload dari library
            upload_video(
                filename=video_path,
                description=description,
                cookies=cookie_path,
                headless=True
            )
            print(f"✅ Berhasil diunggah menggunakan: {cookie_file}")
        except Exception as e:
            # Tangani error dan lanjutkan ke cookie berikutnya
            print(f"❌ Gagal mengunggah dengan {cookie_file}. Alasan: {e}")
            # `continue` tidak diperlukan secara eksplisit di akhir loop,
            # karena loop akan otomatis berlanjut.

    print("\n✨ Semua proses unggah TikTok telah selesai.")

if __name__ == '__main__':
    # Contoh cara menjalankan fungsi ini
    video_file_path = "path/to/your/video.mp4"
    video_description = "Ini deskripsi video TikTok saya! #fyp #trending"
    
    # Pastikan file video ada sebelum menjalankan
    if os.path.exists(video_file_path):
        upload_tiktok(video_path=video_file_path, description=video_description)
    else:
        print(f"File video contoh tidak ditemukan. Harap ubah variabel 'video_file_path' di dalam blok if __name__ == '__main__'.")
