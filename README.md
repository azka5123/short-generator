# Generator Video Pendek dan Upload Otomatis

Aplikasi ini bisa membuat video pendek secara otomatis dan langsung mengunggahnya ke YouTube, Google Drive, dan TikTok.

## Apa yang Bisa Dilakukan
- Membuat video pendek secara otomatis
- Upload video ke YouTube
- Upload video ke Google Drive  
- Upload video ke TikTok
- Menggunakan AI Gemini untuk membuat konten

## Yang Dibutuhkan
- Komputer dengan Python
- Koneksi internet yang stabil
- Akun Google (untuk YouTube dan Google Drive)
- Akun TikTok (jika ingin upload ke TikTok)

## Cara Install dan Setup

### Langkah 1: Download Project
```bash
git clone <alamat-project-ini>
cd <nama-folder-project>
```

### Langkah 2: Siapkan Environment Python
```bash
# Install virtual environment (jika belum ada)
sudo apt install python3-venv

# Buat environment terpisah untuk project ini
python3 -m venv venv

# Aktifkan environment
source venv/bin/activate  # untuk Linux/Mac
# atau
venv\Scripts\activate     # untuk Windows
```

### Langkah 3: Install Library yang Dibutuhkan
```bash
pip install -r requirements.txt
```

### Langkah 4: Buat File Konfigurasi
```bash
# Salin template konfigurasi
cp .env-copy .env

# Edit file konfigurasi
nano .env  # atau buka dengan editor teks lainnya
```

### Langkah 5: Setup Platform Upload

#### Setup YouTube (Opsional)
1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Buat project baru atau pilih project yang ada
3. Aktifkan "YouTube Data API v3"
4. Buat kredensial OAuth 2.0
5. Download file `client_secret.json`
6. Pindahkan file tersebut ke folder `yt_credential/`

#### Setup Google Drive (Opsional)
1. Install rclone:
   ```bash
   # Untuk Ubuntu/Debian
   sudo apt install rclone
   
   # Atau download dari https://rclone.org/downloads/
   ```

2. Setup rclone untuk Google Drive:
   ```bash
   rclone config
   ```

3. Ikuti langkah-langkah berikut:
   - Ketik "n" untuk membuat remote baru
   - Beri nama (misalnya: "gdrive")
   - Pilih "Google Drive" dari daftar
   - Ikuti proses login ke Google
   - Selesaikan setup

4. Test apakah berhasil:
   ```bash
   rclone ls gdrive:
   ```

#### Setup TikTok (Opsional)
1. Install ekstensi browser [Get cookies.txt LOCALLY](https://github.com/kairi003/Get-cookies.txt-LOCALLY)
2. Buka TikTok di browser dan login
3. Klik ekstensi dan export cookies
4. Simpan file cookies sebagai `cookies.txt` di folder `tiktok_cookies/`

## Cara Menggunakan

### Menjalankan Program
```bash
# Pastikan environment aktif
source venv/bin/activate

# Jalankan program
python3 generate_video.py
```

## Struktur Folder Project
```
project/
├── generate_video.py       # Program utama
├── upload_tiktok.py        # Program upload ke TikTok
├── upload_yt.py            # Program upload ke YouTube
├── requirements.txt        # Daftar library yang dibutuhkan
├── .env-copy              # Template konfigurasi
├── .env                   # File konfigurasi utama (buat sendiri)
├── yt_credential/         # Folder untuk file YouTube
│   └── client_secret.json # File kredensial YouTube
├── tiktok_cookies/        # Folder untuk file TikTok
│   └── cookies.txt        # File cookies TikTok
└── venv/                  # Folder environment Python

# File konfigurasi rclone biasanya ada di:
# ~/.config/rclone/rclone.conf (Linux/Mac)
# %APPDATA%/rclone/rclone.conf (Windows)
```

## Pengaturan File .env
```bash
# API Key dari Gemini AI
GEMINI_API_KEY=masukkan_api_key_gemini_disini

# Pengaturan Google Drive
RCLONE_REMOTE_NAME_AND_PATH=gdrive  # nama remote + path folder

# Pengaturan YouTube
YT_ACC=2        # berapa banyak akun YouTube yang akan digunakan
YT_WORKER=2     # berapa banyak video yang diupload bersamaan
```

## Jika Ada Masalah

### Masalah Saat Install
- Pastikan koneksi internet stabil
- Update pip dengan: `pip install --upgrade pip`
- Pastikan Python sudah terinstall dengan benar

### Masalah Login/Authentication
- Periksa API key Gemini di file .env
- Pastikan file `client_secret.json` untuk YouTube sudah benar
- Periksa apakah cookies TikTok masih valid (login ulang jika perlu)
- Test koneksi Google Drive: `rclone ls gdrive:`

### Masalah Upload
- Periksa ukuran file video (jangan terlalu besar)
- Pastikan format video didukung (MP4 biasanya aman)
- Periksa kuota API masih tersedia
- Untuk Google Drive: pastikan rclone sudah dikonfigurasi dengan benar

### Tips Tambahan
- Jika upload gagal, coba upload ulang setelah beberapa menit
- Pastikan semua akun (Google, TikTok) dalam keadaan aktif
- Backup file penting sebelum menjalankan program

## Kontribusi
Jika ada saran perbaikan atau menemukan bug, silakan buat issue atau pull request di repository ini.

## Catatan Penting
- Pastikan menggunakan API key yang valid
- Jangan share file kredensial ke orang lain
- Gunakan program ini sesuai dengan ketentuan masing-masing platform
- Backup data penting sebelum menggunakan program ini