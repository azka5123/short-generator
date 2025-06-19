import asyncio
import edge_tts
from moviepy import *
import os
import random

# Config
SOURCE_FILE = 'source.txt'
RAW_VIDEO_FOLDER = 'raw_vidio'
TTS_AUDIO = 'tts_output.mp3'
VIDEO_SIZE = (720, 1280)  # TikTok Portrait Mode

# 1. Baca text dari source.txt dan buat judul vidio
with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

title = lines[0].strip()               
text = title + '\n' + ''.join(lines[1:]).strip()

OUTPUT_FILE = 'result/' + title + ".mp4"

# 2. Generate TTS pakai pyttsx3
async def generate_tts(text, filename):
    voices = ["en-US-GuyNeural", "en-US-JennyNeural"]  
    selected_voice = random.choice(voices)
    print(f"🔊 Voice terpilih: {selected_voice}") 
    communicate = edge_tts.Communicate(text=text, voice=selected_voice, rate="+15%") 
    await communicate.save(filename)
    
asyncio.run(generate_tts(text, TTS_AUDIO))
audio_clip = AudioFileClip(TTS_AUDIO)
audio_duration = audio_clip.duration

# 3. Ambil satu file video random dari /raw_vidio/
video_files = [f for f in os.listdir(RAW_VIDEO_FOLDER) if f.endswith(('.mp4', '.mov', '.avi'))]
if not video_files:
    raise Exception("❌ Tidak ada video di folder /raw_vidio/")
selected_video = os.path.join(RAW_VIDEO_FOLDER, random.choice(video_files))

# 4. Load dan sesuaikan durasi video
bg_clip = VideoFileClip(selected_video)

# 5 Resize ke TikTok Portrait Mode (9:16)
bg_clip = bg_clip.resized(height=VIDEO_SIZE[1])

# 6 Potong durasi agar sama dengan audio
max_start = bg_clip.duration - audio_duration
start_time = random.uniform(0, max_start)
bg_clip = bg_clip.subclipped(0, audio_clip.duration)

# 7. Gabungkan semua (video + text + audio)
final_clip = CompositeVideoClip([bg_clip])
final_clip = final_clip.with_audio(audio_clip)

# 8. Export video
final_clip.write_videofile(OUTPUT_FILE, fps=24)

# 9. Bersihkan file TTS temporary
os.remove(TTS_AUDIO)

print("✅ Video berhasil dibuat:", OUTPUT_FILE)
