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

## **Choose ONE genre/subreddit style:**

### **Personal & Confessional**
- **r/nosleep** (Horror/Mystery): Psychological tension, supernatural elements, unexplained phenomena
- **r/confession** (Drama/Personal): Raw honesty, life-changing moments, moral dilemmas
- **r/TrueOffMyChest** (Unfiltered Drama): Brutally honest stories, emotional releases, controversial takes
- **r/relationships** (Romance/Drama): Relationship dynamics, emotional growth, human connections
- **r/relationship_advice** (Relationship Drama): Complex relationship problems, seeking guidance
- **r/AskReddit** (Experience/Opinion): Personal experiences shared in response to questions, social discussions

### **Comedy & Fails**
- **r/tifu** (Comedy): Self-deprecating humor, embarrassing situations, comedic timing
- **r/pettyrevenge** (Satisfying Comedy): Small-scale revenge stories, satisfying comebacks
- **r/MaliciousCompliance** (Clever Comedy): Following rules literally with absurd results
- **r/EntitledParents** (Frustrating Comedy): Dealing with unreasonable, entitled behavior
- **r/ChoosingBeggars** (Ridiculous Comedy): Unreasonable people making outrageous demands

### **Horror & Mystery**
- **r/LetsNotMeet** (Real Horror): True scary encounters, dangerous situations avoided
- **r/TwoSentenceHorror** (Micro Horror): Extremely short, punch-line horror stories
- **r/shortscarystories** (Compact Horror): Brief but complete horror narratives

### **Justice & Revenge**
- **r/ProRevenge** (Epic Satisfaction): Long-term, elaborate revenge stories with major consequences
- **r/AmItheAsshole** (Moral Judgment): Presenting situations for community judgment, moral dilemmas

### **Positive & Inspiring**
- **r/wholesomememes** (Heartwarming): Feel-good stories, human kindness, positive outcomes
- **r/HumansBeingBros** (Inspiring): Stories of unexpected kindness, community support
- **r/UnresolvedMysteries** (Thought-provoking): Intriguing unsolved cases, detective work

## **Format Requirements:**
- The story title MUST be written as the first line of the output
- Title must be 5 to 8 words long and match your chosen genre
- After the title, start with an appropriate opening for your chosen subreddit:
  - r/nosleep: "I've never told anyone this before..." 
  - r/confession: "I need to get this off my chest..."
  - r/TrueOffMyChest: "I can't keep this inside anymore..."
  - r/tifu: "This happened yesterday and I'm still cringing..."
  - r/wholesomememes: "Something beautiful happened to me today..."
  - r/relationships: "I never expected this person to change my life..."
  - r/relationship_advice: "I don't know what to do about..."
  - r/AskReddit: "You asked about [topic], here's what happened to me..."
  - r/pettyrevenge: "Someone messed with me, so I got them back..."
  - r/MaliciousCompliance: "They told me to follow the rules exactly..."
  - r/EntitledParents: "I couldn't believe what this parent did..."
  - r/ChoosingBeggars: "This person wanted something for free, then..."
  - r/LetsNotMeet: "I had the creepiest encounter and I'm still shaken..."
  - r/TwoSentenceHorror: [No opening - just two sentences]
  - r/shortscarystories: "This is the scariest thing that ever happened to me..."
  - r/ProRevenge: "Someone wronged me badly, so I spent months planning..."
  - r/AmItheAsshole: "I did something and now everyone's mad at me..."
  - r/HumansBeingBros: "A stranger did something that restored my faith in humanity..."
  - r/UnresolvedMysteries: "There's something that happened that I can't explain..."
- Do NOT put the title in quotation marks

## **Story Requirements:**
- **Length by subreddit**:
  - r/TwoSentenceHorror: Exactly 2 sentences
  - r/shortscarystories: 100-300 words
  - All others: 200-500 words
- First-person perspective
- Match the tone and style expectations of your chosen subreddit
- Build appropriate emotional arc for the genre (suspense, humor, warmth, etc.)
- **Must have a clear, complete ending with resolution**

## **VARIETY ENHANCEMENT ELEMENTS** ⭐

### **Character Diversity Pool** (Pick 1-2 randomly):
- **Age**: Child, teenager, young adult, middle-aged, elderly, very elderly
- **Profession**: Student, teacher, retail worker, office worker, artist, healthcare worker, tradesperson, unemployed, retired, freelancer, small business owner, gig worker, content creator
- **Living situation**: Lives alone, with roommates, with family, in dorms, traveling, homeless, recently moved, long-distance relationship
- **Personality traits**: Introverted/extroverted, anxious/confident, optimistic/pessimistic, organized/chaotic, tech-savvy/traditional, people-pleaser/assertive

### **Setting Variety Wheel** (Choose 1):
- **Urban**: Apartment building, subway, coffee shop, office building, city park, busy street, mall, nightclub
- **Suburban**: Neighborhood, mall, grocery store, local restaurant, community center, garage, HOA meeting
- **Rural**: Small town, farm, forest, lake, mountain cabin, country road, gas station
- **Institutional**: School, hospital, library, gym, church, government building, courthouse
- **Transportation**: Bus, train, airplane, car, bike, walking, rideshare
- **Digital**: Online gaming, social media, video calls, dating apps, forums, work-from-home setup
- **Service/Retail**: Restaurant, store, salon, mechanic shop, bank, post office

### **Conflict Catalyst Options** (Roll for 1):
1. **Misunderstanding/Miscommunication**
2. **Unexpected encounter with stranger**
3. **Technology malfunction/glitch**
4. **Weather/natural event**
5. **Lost/found object**
6. **Overheard conversation**
7. **Wrong place, wrong time**
8. **Family secret revealed**
9. **Childhood memory triggered**
10. **Random act of kindness/cruelty**
11. **Deadline pressure**
12. **Identity mix-up**
13. **Neighbor dispute**
14. **Work drama/office politics**
15. **Social media incident**
16. **Customer service gone wrong**

### **Emotional Journey Arcs** (Select based on genre):
- **Horror**: Comfort → Unease → Fear → Terror → Resolution/Acceptance
- **Comedy**: Confidence → Mistake → Embarrassment → Panic → Humor/Learning
- **Drama**: Stability → Conflict → Crisis → Reflection → Growth
- **Romance**: Loneliness → Meeting → Connection → Challenge → Love
- **Heartwarming**: Sadness → Encounter → Kindness → Joy → Gratitude
- **Revenge**: Wronged → Anger → Planning → Execution → Satisfaction
- **Judgment**: Uncertainty → Situation → Decision → Consequences → Reflection

### **Unique Perspective Twists** (Optional enhancement):
- Unreliable narrator (they misunderstand the situation)
- Multiple POV shifts within the story
- Story told through text messages, emails, or social media posts
- Flashback structure
- Present tense urgency
- Stream of consciousness style
- Update/edit format (common on Reddit)

### **Cultural/Social Context Variety**:
- Different cultural backgrounds and traditions
- Various socioeconomic situations
- Different family structures
- Urban vs rural perspectives
- Generational differences
- International settings or immigrant experiences
- Different educational backgrounds
- Various relationship dynamics (friends, family, romantic, professional)

## **Content Guidelines:**
- Appropriate for social media platforms (TikTok, YouTube, Instagram)
- Avoid: gore, violence, explicit content, abuse, self-harm, illegal activities
- Avoid: religious, political, or controversial real-world topics
- Focus on: psychological elements, human emotions, relatable experiences, universal themes

## **Genre-Specific Enhancement Tips:**
- **Horror/Mystery**: Vary the source of fear (technology, nature, psychology, supernatural, social)
- **Comedy**: Mix physical comedy, situational humor, wordplay, and social awkwardness
- **Romance**: Explore different types of love (first love, rekindled love, friendship-to-romance, unexpected attraction)
- **Drama**: Include moral dilemmas, ethical choices, family dynamics, personal growth
- **Heartwarming**: Show different forms of kindness (strangers, community, family, animals, self-care)
- **Revenge**: Build satisfying payback that feels proportional and clever
- **Judgment**: Present clear moral dilemmas where the right answer isn't obvious

## **Subreddit-Specific Style Notes:**
- **r/AmItheAsshole**: Always end with "So, AITA?" and include enough context for judgment
- **r/TrueOffMyChest**: More raw and unfiltered than r/confession, often controversial
- **r/MaliciousCompliance**: Focus on clever literal interpretation of rules
- **r/ChoosingBeggars**: Include ridiculous demands and entitled behavior
- **r/ProRevenge**: Build up the offense and make the revenge elaborate and satisfying
- **r/LetsNotMeet**: Emphasize real danger and genuine fear
- **r/UnresolvedMysteries**: Present facts objectively, leave questions unanswered

## **Creativity Boosters:**
- **Random Element Generator**: Include one unexpected detail that doesn't typically belong in your chosen genre
- **Sensory Focus**: Pick one sense to emphasize throughout the story (sight, sound, smell, touch, taste)
- **Time Constraint**: Give your story a specific timeframe (24 hours, one week, during a single conversation)
- **Object Significance**: Choose a mundane object that becomes symbolically important
- **Reverse Expectation**: Start with one genre expectation, then subvert it

## **Final Variety Check:**
Before writing, randomly select:
1. One character trait that's opposite to what you'd normally choose
2. One setting you've never written about before
3. One emotional outcome that challenges the typical genre expectations
4. One cultural or social element different from your usual perspective
5. One modern element (technology, social media, current trends) that affects the story
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