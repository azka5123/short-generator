  # AI-Powered Social Media Video Generator

  This project automates the creation and uploading of short-form videos for social media platforms like TikTok and YouTube. It can generate content in two ways: by scraping stories from Reddit or by generating original stories using the Gemini AI. The script then combines the story with a random background video, adds AI-generated voice narration and subtitles, and uploads the final product.

  ## Features

  - **Content Sourcing**:
    - **Reddit Crawler**: Fetches top stories from specified subreddits.
    - **AI Story Generation**: Creates original, engaging short stories using a detailed AI prompt.
  - **Content Safety**: Validates stories using Gemini AI to ensure they are safe for posting and won't lead to platform bans.
  - **Automated Video Production**:
    - Converts text to speech using Microsoft Edge's TTS for natural-sounding narration.
    - Automatically generates synchronized subtitles (`.srt`).
    - Overlays subtitles onto a randomly selected background video from your library.
    - Formats videos to the standard 9:16 portrait aspect ratio.
  - **Multi-Platform Uploading**:
    - Uploads the finished video to multiple TikTok accounts.
    - Uploads the finished video to multiple YouTube channels.
    - Backs up the video to a specified Google Drive folder using `rclone`.
  - **Customization**: Easily configurable through an `.env` file.

  ## Workflows

  There are two main workflows to generate content:

  ### 1. Reddit-Based Video Generation

  This workflow uses stories scraped from Reddit.

  1.  **`python crawl_story.py`**: Scrapes stories from the subreddits defined in your `.env` file and saves them as `.txt` files in the `story/` directory.
  2.  **`python validate_story.py`**: Checks the stories in the `story/` directory for content safety. Safe stories are moved to the `validate_story/` directory, while unsafe ones are deleted.
  3.  **`python generate_vidio_from_reddit.py`**: Picks a random story from `validate_story/`, generates a video, uploads it to all configured platforms, and then deletes the temporary files.

  ### 2. AI-Based Video Generation

  This workflow generates a new story from scratch using AI.

  -   **`python generate_vidio_from_ai.py`**: Prompts the Gemini AI to write a new story, generates a video from it, uploads it to all platforms, and cleans up the temporary files.

  ## Setup and Installation

  ### Prerequisites
  -   `python`
  -   `pip` and `venv`
  -   `rclone` (for Google Drive backups)

  ### 1. Clone the Repository

  ```bash
  git clone https://github.com/azka5123/short-generator.git
  cd short-generator
  ```

  ### 2. Create a Virtual Environment

  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
  ```

  ### 3. Install Dependencies

  ```bash
  pip install -r requirements.txt
  ```

  ### 4. Configure Environment Variables

  Copy the example `.env` file:

  ```bash
  cp .env-copy .env
  ```

  Now, edit the `.env` file with your own credentials and settings.

  ### 5. Directory and Credential Setup

  -   **Background Videos**: Place your `.mp4` background videos (e.g., gameplay footage, satisfying clips) into the `raw_vidio/` folder.
  -   **Fonts**: The project uses the DejaVu Sans font located in `fonts/`. You can change the font in the `.env` file.
  -   **TikTok Cookies**:
      -   For each TikTok account you want to upload to, get its `cookies.txt` file using a browser extension like "Get cookies.txt".
      -   Place each `cookies.txt` file inside the `tiktok_cookies/` directory. The script will upload to every account it finds a cookie for.
  -   **YouTube Credentials**:
      -   Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
      -   Enable the "YouTube Data API v3".
      -   Create OAuth 2.0 Client IDs credentials and download the `client_secret.json` file.
      -   Place the `client_secret.json` file in the `yt_credential/` directory.
      -   The first time you run a script that uploads to YouTube, you will be prompted to authenticate each account in your browser. A `token.json` file will be created for each account in its respective `yt_credential/acc*/` folder.
  -   **Rclone (Google Drive)**:
      -   Configure `rclone` with your Google Drive account.
      -   Set the `RCLONE_REMOTE_NAME_AND_PATH` in your `.env` file to the name of your rclone remote and the path where you want to save the videos (e.g., `gdrive:MyVidioBackup/`).

  ## Usage

  After completing the setup, you can run the scripts as described in the [Workflows](#workflows) section.

  **Example (Reddit Workflow):**

  ```bash
  # Step 1: Get stories
  python crawl_story.py
  ```
  > **Note:** If you have trouble accessing Reddit because of regional blocks, you can use a VPN or run the script with `torsocks`:
  > `sudo apt install tor`
  > `torsocks python crawl_story.py`

  ```bash
  # Step 2: Validate stories
  python validate_story.py

  # Step 3: Generate and upload video
  python generate_vidio_from_reddit.py
  ```

  **Example (AI Workflow):**

  ```bash
  # Generate a story, create a video, and upload it in one go
  python generate_vidio_from_ai.py
  ```

  ## File Descriptions

  -   `crawl_story.py`: Fetches stories from Reddit.
  -   `validate_story.py`: Checks if stories are safe for social media.
  -   `generate_vidio_from_reddit.py`: Creates a video from a validated Reddit story.
  -   `generate_vidio_from_ai.py`: Creates a video from an AI-generated story.
  -   `upload_tiktok.py`: Handles video uploads to TikTok accounts.
  -   `upload_yt.py`: Handles video uploads to YouTube channels.
  -   `requirements.txt`: A list of all the Python packages required for this project.
  -   `.env-copy`: An example environment file.
