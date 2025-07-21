from dotenv import load_dotenv
import asyncio
import edge_tts
from moviepy import *
import os
import random
import subprocess
import pysrt
from upload_yt import start_async_upload
from upload_tiktok import upload_tiktok
import glob
import re

# ================== CONFIG ==================
load_dotenv()
RAW_VIDEO_FOLDER = os.getenv('RAW_VIDIO_DIR')
VALIDATED_FOLDER = os.getenv('VALIDATE_STORY_DIR')
TTS_AUDIO = 'tts_output.mp3'
TTS_SUBTITLE = 'tts_output.srt'
VIDEO_SIZE = (1080, 1920)  # TikTok Portrait Mode
OUTPUT_FOLDER = os.getenv('OUTPUT_VIDIO_DIR')
GDRIVE_FOLDER = os.getenv('RCLONE_REMOTE_NAME_AND_PATH')
FONTS = os.getenv('FONTS')
HASHTAGS = os.getenv('HASHTAGS')
# ============================================


# ========== 1. Load Story from validate_story ==========
story_files = glob.glob(os.path.join(VALIDATED_FOLDER, '*.txt'))
if not story_files:
    raise Exception("❌ No stories in validate_story folder.")

story_path = random.choice(story_files)
print(f"📝 Selected story: {story_path}")
with open(story_path, 'r', encoding='utf-8') as f:
    lines = f.read().strip().split('\n')

title = lines[0].strip()
text = title + '\n' + '\n'.join(lines[1:]).strip()

# Create a safe output filename
def slugify(text):
    return re.sub(r'[^a-zA-Z0-9]+', '_', text).strip("_")

OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, slugify(title) + ".mp4")

# ========== 2. Generate TTS and Subtitle ==========
async def generate_tts(text, filename, subtitle):
    voices = ["en-US-GuyNeural", "en-US-JennyNeural", "en-US-AriaNeural", "en-IE-ConnorNeural"]
    selected_voice = random.choice(voices)
    print(f"🔊 Selected voice: {selected_voice}")

    communicate = edge_tts.Communicate(text=text, voice=selected_voice, rate="+15%")
    submaker = edge_tts.SubMaker()

    with open(filename, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    with open(subtitle, "w", encoding="utf-8") as sub_file:
        sub_file.write(submaker.get_srt())

asyncio.run(generate_tts(text, TTS_AUDIO, TTS_SUBTITLE))
audio_clip = AudioFileClip(TTS_AUDIO)
audio_duration = audio_clip.duration

# ========== 3. Load Random Background Video ==========
video_files = [f for f in os.listdir(RAW_VIDEO_FOLDER) if f.endswith(('.mp4', '.mov', '.avi'))]
print(f"🎬 Found {len(video_files)} videos in raw_vidio folder.")
if not video_files:
    raise Exception("❌ No videos in raw_vidio folder.")
selected_video = os.path.join(RAW_VIDEO_FOLDER, random.choice(video_files))
bg_clip = VideoFileClip(selected_video)

# Resize to TikTok format
bg_clip = bg_clip.resized(height=VIDEO_SIZE[1], width=VIDEO_SIZE[0])

# Trim to audio duration
max_start = bg_clip.duration - audio_duration
start_time = random.uniform(0, max_start)
bg_clip = bg_clip.subclipped(start_time, start_time + audio_duration)

# ========== 4. Generate Subtitle VideoClip ==========
subs = pysrt.open(TTS_SUBTITLE)
subtitles = []
for sub in subs:
    start = sub.start.ordinal / 1000
    end = sub.end.ordinal / 1000
    duration = end - start
    text = sub.text.replace('\n', ' ')

    txt_clip = TextClip(
        text=text,
        font_size=100,
        font=FONTS,
        color='white',
        stroke_color='black',
        stroke_width=12,
        method='caption',
        size=(VIDEO_SIZE[0]-100, None),
        margin=(50,50)
    ).with_start(start).with_duration(duration)
    text_position = ('center',750)

    subtitles.append(txt_clip.with_position(text_position))

# ========== 5. Combine video, audio, and subtitles ==========
final_clip = CompositeVideoClip([bg_clip, *subtitles])
final_clip = final_clip.with_audio(audio_clip)

# ========== 6. Export the resulting video ==========
final_clip.write_videofile(
    OUTPUT_FILE,
    fps=30,
    codec='libx264',
    audio_codec='aac',
    threads=4,
    preset='slow',
    bitrate='8000k',
)
print("✅ Video successfully created:", OUTPUT_FILE)

# ========== 7. Upload to Google Drive ==========
try:
    print("🚀 Uploading to Google Drive...")
    subprocess.run(['rclone', 'copy', OUTPUT_FILE, GDRIVE_FOLDER], check=True)
    print("✅ Upload to Google Drive complete.")
except subprocess.CalledProcessError as e:
    print("❌ Failed to upload to Google Drive:", e)

# ========== 8. Upload to YouTube ==========
start_async_upload(OUTPUT_FILE, title, HASHTAGS)

# ========== 9. Upload to TikTok ==========
full_description = f"{title}\n{HASHTAGS}"
upload_tiktok(OUTPUT_FILE, full_description)

# ========== 10. Cleanup ==========
os.remove(OUTPUT_FILE)
os.remove(TTS_AUDIO)
os.remove(TTS_SUBTITLE)
os.remove(story_path)
print("🧹 Temporary files deleted.")
