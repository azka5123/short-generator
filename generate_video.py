import asyncio
import edge_tts
from moviepy import *
import os
import random
from google import genai
import subprocess
from upload_yt import start_async_upload 
import re
import pysrt
from upload_tiktok import upload_tiktok

# Config
RAW_VIDEO_FOLDER = 'raw_vidio'
TTS_AUDIO = 'tts_output.mp3'
VIDEO_SIZE = (1080, 1920)  # TikTok Portrait Mode
GDRIVE_FOLDER = 'gdrive:story'  # Rclone remote:path
FONTS = "fonts/dejavu-sans/DejaVuSans.ttf"
TTS_SUBTITLE = "tts_output.srt"

# 1. Generate story
client = genai.Client(api_key=os.getenv('GEMINI_API'))
prompt = """
Write an original short story in the style of a Reddit post from one of the following subreddit communities:

**Choose ONE genre/subreddit style:**
- **r/nosleep** (Horror/Mystery): Psychological tension, supernatural elements, unexplained phenomena
- **r/confession** (Drama/Personal): Raw honesty, life-changing moments, moral dilemmas
- **r/tifu** (Comedy): Self-deprecating humor, embarrassing situations, comedic timing
- **r/wholesomememes** (Heartwarming): Feel-good stories, human kindness, positive outcomes
- **r/relationships** (Romance/Drama): Relationship dynamics, emotional growth, human connections

## Format Requirements:
- The story title MUST be written as the first line of the output
- Title must be 5 to 8 words long and match your chosen genre
- After the title, start with an appropriate opening for your chosen subreddit:
  - r/nosleep: "I've never told anyone this before..." 
  - r/confession: "I need to get this off my chest..."
  - r/tifu: "This happened yesterday and I'm still cringing..."
  - r/wholesomememes: "Something beautiful happened to me today..."
  - r/relationships: "I never expected this person to change my life..."
- Do NOT put the title in quotation marks

## Story Requirements:
- 200-500 words
- First-person perspective
- Match the tone and style expectations of your chosen subreddit
- Build appropriate emotional arc for the genre (suspense, humor, warmth, etc.)
- **Must have a clear, complete ending with resolution**

## Content Guidelines:
- Appropriate for social media platforms (TikTok, YouTube, Instagram)
- Avoid: gore, violence, explicit content, abuse, self-harm, illegal activities
- Avoid: religious, political, or controversial real-world topics
- Focus on: psychological elements, human emotions, relatable experiences, universal themes

## Genre-Specific Tips:
- **Horror/Mystery**: Build tension through atmosphere and psychological elements rather than violence
- **Comedy**: Use timing, relatability, and self-awareness for humor
- **Romance**: Focus on emotional connection and character development
- **Drama**: Explore authentic human experiences and personal growth
- **Heartwarming**: Highlight human kindness and positive human nature
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

generated_text = response.text

# generated_text ="""
# The Whisper in My Closet
# I’ve never told anyone this before. Two weeks ago, every night, 
# I heard a faint whisper coming from my closet—soft, low, like someone calling my name.
# """

lines = generated_text.strip().split('\n')
title = lines[0].strip()               
text = title + '\n' + '\n'.join(lines[1:]).strip()

OUTPUT_FILE = 'result/' + title + ".mp4"

# 2. Generate TTS And Subtitle Using pyttsx3
async def generate_tts(text, filename, subtitle):
    voices = ["en-US-GuyNeural", "en-US-JennyNeural", "en-US-AriaNeural", "en-IE-ConnorNeural"]  
    selected_voice = random.choice(voices)
    print(f"🔊 Voice terpilih: {selected_voice}") 

    communicate = edge_tts.Communicate(text=text, voice=selected_voice, rate="+15%")
    submaker = edge_tts.SubMaker()

    # Stream langsung ke file + submaker
    with open(filename, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    # Simpan subtitle SRT
    with open(subtitle, "w", encoding="utf-8") as sub_file:
        sub_file.write(submaker.get_srt())
    
asyncio.run(generate_tts(text, TTS_AUDIO,TTS_SUBTITLE))
audio_clip = AudioFileClip(TTS_AUDIO)
audio_duration = audio_clip.duration

# 3. Get And Load A Random Video
video_files = [f for f in os.listdir(RAW_VIDEO_FOLDER) if f.endswith(('.mp4', '.mov', '.avi'))]
if not video_files:
    raise Exception("❌ Tidak ada video di folder /raw_vidio/")
selected_video = os.path.join(RAW_VIDEO_FOLDER, random.choice(video_files))
bg_clip = VideoFileClip(selected_video)

# 4 Resize To TikTok Portrait Mode (9:16)
bg_clip = bg_clip.resized(height=VIDEO_SIZE[1], width=VIDEO_SIZE[0])

# 5 Cut Video To Audio Duration
max_start = bg_clip.duration - audio_duration
start_time = random.uniform(0, max_start)
bg_clip = bg_clip.subclipped(start_time, start_time + audio_clip.duration)

# 6. Load Subtitle From SRT File
subs = pysrt.open(TTS_SUBTITLE)

subtitles = []
for sub in subs:
    start = sub.start.ordinal / 1000
    end = sub.end.ordinal / 1000
    duration = end - start
    text = sub.text.replace('\n', ' ')

    txt_clip = TextClip(
        text=text,
        font_size=90,
        font=FONTS,
        color='white',
        stroke_color='black',
        stroke_width=10,
        method='caption',
        size=(VIDEO_SIZE[0]-100, None),
        margin=(50,50)
    ).with_start(start).with_duration(duration)
    text_position = ('center',750) 
              
    subtitles.append(txt_clip.with_position(text_position))

# 7. Combine All (video + subtitle + audio)
final_clip = CompositeVideoClip([bg_clip, *subtitles])
final_clip = final_clip.with_audio(audio_clip)

# 8. Export video
final_clip.write_videofile(
    OUTPUT_FILE,
    fps=30,
    codec='libx264',
    audio_codec='aac',
    threads=4,
    preset='slow',
    logger='none'
)
print("✅ Video berhasil dibuat:", OUTPUT_FILE)

# 9. Upload To Google Drive via rclone
try:
    print("🚀 Mengunggah ke Google Drive...")
    subprocess.run(['rclone', 'copy', OUTPUT_FILE, GDRIVE_FOLDER], check=True)
    print("✅ Upload ke Google Drive selesai.")
except subprocess.CalledProcessError as e:
    print("❌ Gagal upload ke Google Drive:", e)

# # 10. Upload To YouTube
deskripsi = "#story #storytime #reddit #redditstories #fyp"
start_async_upload(OUTPUT_FILE, title, deskripsi)
# # start_async_upload("result/testing.mp4", "Testing", deskripsi)

# 11. Upload To Tiktok
full_description = f"{title}\n{deskripsi}"
upload_tiktok(OUTPUT_FILE, full_description)

#12. Delete File Video, TTS Temporary And Subtitle File
os.remove(OUTPUT_FILE)
os.remove(TTS_AUDIO)
os.remove(TTS_SUBTITLE)