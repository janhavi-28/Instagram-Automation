# Instagram Automation

An automated Instagram posting bot built with Python and [Playwright](https://playwright.dev/python/). 
This bot physically simulates human interactions within a hidden web browser to natively upload photos and videos to Instagram without triggering restrictive API blocks.

## Features
- **Browser Automation:** Uses Playwright with the Microsoft Edge channel to bypass Instagram's strict bot detection and avoid login_required bans typically caused by unofficial APIs like `aiograpi`.
- **Media Support:** Seamlessly handles both Images (`.jpg`, `.jpeg`, `.png`) and Videos (`.mp4`).
- **Smart Captions:** Automatically loads captions from a matching `.txt` file alongside the media file, or falls back to a generic default caption.
- **Auto-Archiving:** Automatically moves successfully uploaded media and their captions to an `archive` folder so they are never posted twice.
- **Scheduling:** Run jobs instantly or rely on an integrated Python schedule.

## Folder Structure
```text
.
├── config.py           # Configuration file (Credentials, delays)
├── dashboard.py        # Streamlit Web UI dashboard
├── main.py             # Entrypoint script for scheduling and ad-hoc uploads
├── uploader.py         # The core Playwright browser automation logic
├── logger.py           # Custom logging utility
├── photos/             # Place photos here (e.g. image.jpg + image.txt)
├── videos/             # Place videos here (e.g. video.mp4 + video.txt)
├── reels/              # Place reels here
├── archive/            # Successfully uploaded files are moved here
└── sessions/           # Automatically stores browser cookies and state
```

## Setup & Installation

1. **Install Python Requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers:**
   ```bash
   playwright install
   ```
   *(Note: This project is explicitly configured to use your system's installed Microsoft Edge browser for H.264 video codec support, which default Playwright Chromium lacks).*

3. **Configure Credentials:**
   Edit the `config.py` file with your Instagram login details:
   ```python
   USERNAME = "your_email_or_username"
   PASSWORD = "your_password"
   ```

## Usage

### Uploading a Post Instantly
1. Place your media file (e.g., `my_vacation.jpg`) into the `photos/` folder.
2. (Optional) Create a text file with the exact same name (e.g., `my_vacation.txt`) in the same folder containing your caption.
3. Run the bot immediately:
   ```bash
   python main.py --now
   ```

### Running the Scheduler
If you want the bot to stay alive in the background and upload based on your configured `scheduler.py` times:
```bash
python main.py
```

### Dashboard UI
Launch the interactive Streamlit dashboard to monitor uploads:
```bash
streamlit run dashboard.py
```

## How It Works
Instead of making raw HTTP requests to Instagram's locked-down API endpoints, this script opens a real instance of Microsoft Edge. It navigates to `instagram.com`, logs into your account, and uses the native `expect_file_chooser()` API to mimic a human clicking the "Select from computer" button. It handles all Instagram pop-ups natively (like the Reels prompt) ensuring the highest success rate possible.
