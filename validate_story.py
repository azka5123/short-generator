# validate_stories.py
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import shutil

# ========== SETUP ==========
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API'))
client = genai.GenerativeModel("gemini-2.5-pro", 
    generation_config={"temperature": 0.2},
    safety_settings={"HARASSMENT": "block_none", "HATE": "block_none"}
)

story_dir = Path(os.getenv('STORY_DIR') )
validate_dir = Path(os.getenv('VALIDATE_STORY_DIR') )
validate_dir.mkdir(exist_ok=True)

# ========== CEK AMAN ==========
def is_safe_content(text):
    prompt = f"""
    Is the following story safe to post on TikTok, YouTube, and Instagram without getting banned?
    Only answer Yes or No.
    if the story use language that is not English, answer no.
    if the story contains any link to external website, answer no.
    if the story too short less than 120 words, answer no.
    Story:
    {text[:3000]}
    """
    try:
        response = client.generate_content(prompt)
        answer = response.text.strip().lower()
        return "yes" in answer and "no" not in answer
    except Exception as e:
        print(f"⚠️ Gemini error: {e}")
        return False

# ========== VALIDASI FILE ==========
for file in story_dir.glob("*.txt"):
    try:
        content = file.read_text()
        print(f"🔍 Checking {file.name}...")
        if is_safe_content(content):
            shutil.move(str(file), validate_dir / file.name)
            print(f"[✅ VALIDATED] {file.name}")
        else:
            os.remove(str(file))
            print(f"[❌ UNSAFE] {file.name}")
    except Exception as e:
        print(f"⚠️ Error reading {file.name}: {e}")
