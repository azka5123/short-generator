import asyncio
import edge_tts
from moviepy import *
import os
import random
from google import genai

# Config
RAW_VIDEO_FOLDER = 'raw_vidio'
TTS_AUDIO = 'tts_output.mp3'
VIDEO_SIZE = (1080, 1920)  # TikTok Portrait Mode

# 1. Generate story
client = genai.Client(api_key=os.getenv('GEMINI_API'))
prompt = """
Write an original short story in the style of a Reddit post from the r/nosleep or r/confession subreddit.

Important rules:
- The story title MUST be written as the first line of the output. 
- The title must be 5 to 8 words long and provide a clear, interesting summary of the story.
- After the title, write the story starting from a casual opening sentence like: ‘I’ve never told anyone this before…’ or ‘This happened to me last summer…’.
- Do NOT put the title in quotation marks or any special format. Just plain text.
- Example of title placement:
  My Strange Neighbor Who Talks to Dolls
  I’ve never told anyone this before, but when I moved to...

Story rules:
- The story must be between 200 to 500 words.
- Use first-person perspective as if the narrator is sharing a real-life, mysterious, strange, or unsettling experience.
- Build suspense gradually with odd or unexplained details.
- The story must have a clear and complete ending, without any cliffhangers or unresolved mysteries.

Content restrictions:
- Avoid gore, violence, explicit content, abuse, self-harm, suicide, and illegal activities.
- Avoid religious, political, or real-world controversial topics.
- Must be appropriate for social media platforms like TikTok, YouTube, and Instagram.
- Mystery, horror, or supernatural elements should focus on psychological tension, strange coincidences, or unexplained but harmless phenomena.

End the story with a clear and satisfying resolution.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

generated_text = response.text

lines = generated_text.strip().split('\n')
title = lines[0].strip()               
text = title + '\n' + '\n'.join(lines[1:]).strip()

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
bg_clip = bg_clip.resized(height=VIDEO_SIZE[1], width=VIDEO_SIZE[0])

# 6 Potong durasi agar sama dengan audio
max_start = bg_clip.duration - audio_duration
start_time = random.uniform(0, max_start)
bg_clip = bg_clip.subclipped(start_time, start_time + audio_clip.duration)

# 7. Gabungkan semua (video + text + audio)
final_clip = CompositeVideoClip([bg_clip])
final_clip = final_clip.with_audio(audio_clip)

# 8. Export video
final_clip.write_videofile(
    OUTPUT_FILE,
    fps=30,
    codec='libx264',
    audio_codec='aac',
    threads=4,
    preset='slow',
)

# 9. Bersihkan file TTS temporary
os.remove(TTS_AUDIO)

print("✅ Video berhasil dibuat:", OUTPUT_FILE)
