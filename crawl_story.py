# reddit_crawler.py
import praw
import os
from pathlib import Path
from dotenv import load_dotenv
import subprocess

# ========== SETUP ==========
load_dotenv()
client_id = os.getenv('CLIENT_ID_REDDIT')
client_secret = os.getenv('CLIENT_SECRET_REDDIT')
user_agent = os.getenv('USER_AGENTS')
GDRIVE_FOLDER = os.getenv('RCLONE_REMOTE_NAME_AND_PATH')
story_dir = Path(os.getenv('STORY_DIR') )
story_dir.mkdir(exist_ok=True)
used_ids_file = os.getenv('USED_IDS_FILE', 'used_ids.txt')

# ========== INITIALIZATION ==========
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent,
)

# Load used IDs
used_ids = set()
if os.path.exists(used_ids_file):
    with open(used_ids_file, "r") as f:
        used_ids = set(f.read().splitlines())

# ========== CONFIG ==========
subreddits = os.getenv("SUBREDDITS").split(",")

stories_per_sub = int(os.getenv("STORIES_PER_SUB" or 5))
max_per_sub = int(os.getenv("MAX_PER_SUB" or 25))

new_used_ids = set()

# ========== SCRAPE ==========
for subreddit_name in subreddits:
    subreddit = reddit.subreddit(subreddit_name)
    count = 0
    print(f"\n🔍 Checking r/{subreddit_name}...")
    for submission in subreddit.top(time_filter='all', limit=max_per_sub):
        if submission.id in used_ids or submission.stickied:
            continue
        if not submission.is_self or len(submission.selftext.strip()) < 200:
            continue

        story_path = story_dir / f"{submission.id}.txt"
        with open(story_path, "w") as f:
            f.write(f"{submission.title}\n\n{submission.selftext}")
        print(f"[💾 SAVED] {story_path.name}")
        new_used_ids.add(submission.id)
        count += 1

        if count >= stories_per_sub:
            break

# ========== SAVE USED ID ==========
used_ids.update(new_used_ids)
with open(used_ids_file, "w") as f:
    f.write("\n".join(used_ids))

# ========= UPLOAD USED IDS TO GDRIVE ==========
try:
    subprocess.run(['rclone', 'copy', used_ids_file, GDRIVE_FOLDER], check=True)
    print("✅ used_ids.txt uploaded to Google Drive.")
except subprocess.CalledProcessError as e:
    print("❌ Upload failed:", e)

