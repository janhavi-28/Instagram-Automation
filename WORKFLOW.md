# Instagram Automation - Workflow Documentation

This document describes the end-to-end workflow and inner workings of the Instagram Automation bot.

## 1. High-Level Architecture

The bot is designed to upload images and videos natively to Instagram using a simulated Microsoft Edge browser. This avoids restrictive API limitations and mimics human interaction.

**Core Components:**
- **`main.py`**: The entry point. Handles CLI arguments to decide whether to run instantly or start the schedule.
- **`scheduler.py`**: A background process that triggers the upload process at intervals defined in `config.py`.
- **`uploader.py`**: The core logic using Playwright to control the browser, log in, handle pop-ups, upload files, and enter captions.
- **`config.py`**: Stores credentials and scheduling intervals.
- **`logger.py`**: Handles console and file logging.
- **`dashboard.py`**: An interactive Streamlit web UI to monitor the bot's status and logs.

## 2. Directory Structure & Media Flow

The bot relies on a specific directory structure to manage its state:

1. **Input Folders**: Users place their `.jpg`, `.png`, `.jpeg`, `.webp`, or `.mp4`/`.mov` files in the `photos/`, `videos/`, or `reels/` directories.
2. **Captions Folders**: Captions can be defined globally in `.txt` files in the `captions/` folder.
3. **Session State**: The `sessions/` directory holds the Playwright browser cookies (`state.json`) to persist logins across runs.
4. **Archiving**: After a successful upload, the media file is automatically moved to the corresponding subdirectory inside the `archive/` folder (`archive_photos`, `archive_reels`, or `archive_videos`) to ensure no duplicate postings.

## 3. Detailed Execution Workflow

### A. Initialization
When `python main.py` is executed:
- If `--now` is passed: The bot bypasses the scheduler and immediately instantiates `InstagramUploader`.
- If no arguments are passed: The script calls `run_scheduler()`, which sets a timer (e.g., every X hours) using the `schedule` library. Once triggered, it runs the `job()` function, which instantiates `InstagramUploader`.

### B. Authentication (`login()`)
1. **Start Browser**: Playwright launches Microsoft Edge with automated flags disabled.
2. **Session Verification**: The browser loads `sessions/state.json` if available.
3. **Navigate to Instagram**: The bot goes to `instagram.com`. If it detects the "Home" or "New post" icons, the session is valid and login is skipped.
4. **Login Execution**: 
   - Accepts/Declines cookies if prompted.
   - If the "Continue as saved profile" button is present, it attempts to click it and potentially enter the password.
   - Otherwise, it fills in the Username and Password from `config.py` into the login form and submits.
5. **Session Saving**: After successful authentication, the browser state is saved back to `sessions/state.json`.

### C. Media Selection and Captioning
Before interacting with the UI for upload:
1. The bot scans `photos/`, `reels/`, and `videos/` for valid extensions.
2. It selects a random media file from the available pool.
3. If a `.webp` photo is selected, it is temporarily converted to `.jpg` using PIL, because Instagram does not natively accept WEBP via the upload dialog.
4. **Caption Generation**:
   - It reads available `.txt` files in `captions/`.
   - It looks at the media filename and attempts to categorize it (e.g., "sunset" -> `nature`, "code" -> `tech`) to select the appropriate `config.HASHTAG_CATEGORIES`.
   - The selected random caption is concatenated with the generated hashtags.

### D. Upload Process (`upload_media()`)
1. **Navigate to Home**: The bot ensures it's on the Instagram home page.
2. **Open Create Dialog**: It clicks the "New post" button (the `+` icon).
3. **File Selection**: It hooks into Playwright's `expect_file_chooser()` and clicks "Select from computer", passing the absolute path of the chosen file.
4. **Post-Processing Prompts**:
   - Clicks "Next" to bypass cropping.
   - For videos, automatically detects and dismisses the "Video posts are now shared as reels" modal if it appears.
   - Clicks "Next" again to bypass filters.
5. **Caption Entry**: The bot locates the caption textbox and fills it with the generated text.
6. **Publish**: The "Share" button is clicked.
7. **Verification**: The bot waits for the success message (e.g., "Your post has been shared").

### E. Post-Upload (Archiving)
Once successfully shared:
- The browser is closed.
- `_archive_file()` moves the original media file from its input directory into the corresponding `archive/` directory. If a file with the same name exists, it appends an incremental counter to the filename to prevent overwriting.
- If a temporary converted `.jpg` file was created, it is deleted.

## 4. Error Handling
- Playwright functions use explicit timeouts to prevent infinite hanging.
- If login fails or gets stuck on a 2FA prompt, a screenshot (`debug_login_error_current.png`) is saved, and the bot exits gracefully.
- If an upload fails, a screenshot (`debug_upload_error_current.png`) is saved to help diagnose the UI state.
