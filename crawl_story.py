# reddit_crawler.py
import praw
import os
from pathlib import Path
from dotenv import load_dotenv
import subprocess
import re

# ========== SETUP ==========
load_dotenv()
client_id = os.getenv('CLIENT_ID_REDDIT')
client_secret = os.getenv('CLIENT_SECRET_REDDIT')
user_agent = os.getenv('USER_AGENTS')
GDRIVE_FOLDER = os.getenv('RCLONE_REMOTE_NAME_AND_PATH')
story_dir = Path(os.getenv('STORY_DIR'))
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
stories_per_sub = int(os.getenv("STORIES_PER_SUB") or 5)
max_per_sub = int(os.getenv("MAX_PER_SUB") or 25)

new_used_ids = set()

# ========== HELPER FUNCTION ==========
def extract_linked_post_ids(text):
    reddit_link_regex = r"https?://(?:www\.)?reddit\.com/r/[^/]+/comments/([a-z0-9]{6,})"
    return re.findall(reddit_link_regex, text)

def clean_reddit_links(text):
    return re.sub(r"https?://(?:www\.)?reddit\.com/r/[^/]+/comments/[a-z0-9]{6,}", "", text)

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

        new_used_ids.add(submission.id)
        main_title = submission.title.strip()
        main_text = submission.selftext.strip()

        linked_ids = extract_linked_post_ids(main_text)

        if linked_ids:
            # get the first linked post
            first_linked_id = linked_ids[0]
            try:
                linked_post = reddit.submission(id=first_linked_id)
                if linked_post.is_self and len(linked_post.selftext.strip()) > 100:
                    print(f"   ↩️ Found linked post (as main): {first_linked_id}")
                    main_title = linked_post.title.strip()
                    main_text = linked_post.selftext.strip()
                    new_used_ids.add(linked_post.id)

                    # Add the linked post text to the main text
                    main_text += f"\n\n{submission.selftext.strip()}"
            except Exception as e:
                print(f"   ⚠️ Failed to fetch linked post {first_linked_id}: {e}")

        # Clean up Reddit links in the main text
        cleaned_text = clean_reddit_links(main_text)

        # save the story id
        story_path = story_dir / f"{submission.id}.txt"
        with open(story_path, "w") as f:
            f.write(f"{main_title}\n\n{cleaned_text}")
        print(f"[💾 SAVED] {story_path.name}")

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
