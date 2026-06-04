import os
import json
import random
import shutil
import time
import asyncio
from pathlib import Path
from playwright.sync_api import sync_playwright
import config
from logger import log_info, log_error, log_warning

class InstagramUploader:
    def __init__(self):
        self.session_file = "sessions/state.json"
        os.makedirs("sessions", exist_ok=True)
        
        self.dirs = {
            "photos": "photos",
            "reels": "reels",
            "videos": "videos",
            "captions": "captions",
            "archive_photos": "archive/photos",
            "archive_reels": "archive/reels",
            "archive_videos": "archive/videos"
        }
        for d in self.dirs.values():
            os.makedirs(d, exist_ok=True)
            
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start_browser(self):
        self.playwright = sync_playwright().start()
        # Launch browser (headless=False for debugging, True for production)
        # We must use 'msedge' or 'chrome' channel so proprietary video codecs (h264) work on Instagram's web UI
        self.browser = self.playwright.chromium.launch(
            channel="msedge",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        if os.path.exists(self.session_file):
            self.context = self.browser.new_context(storage_state=self.session_file, locale="en-US")
        else:
            self.context = self.browser.new_context(locale="en-US")
            
        self.page = self.context.new_page()

    def close_browser(self):
        if self.context:
            self.context.storage_state(path=self.session_file)
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def login(self):
        if not config.USERNAME or not config.PASSWORD:
            log_error("Credentials not set in config.py")
            return False

        self.start_browser()
        
        try:
            log_info("Navigating to Instagram to verify session...")
            self.page.goto("https://www.instagram.com/", timeout=60000)
            time.sleep(3)
            
            # Check if already logged in
            if self.page.locator("svg[aria-label='Home']").count() > 0 or self.page.locator("svg[aria-label='New post']").count() > 0:
                log_info("Session valid. Logged in successfully.")
                self.close_browser()
                return True
                
            log_info(f"Logging in with credentials for {config.USERNAME}...")
            
            if self.page.locator("text='Allow all cookies'").count() > 0:
                self.page.locator("text='Allow all cookies'").click()
                time.sleep(2)
            elif self.page.locator("text='Decline optional cookies'").count() > 0:
                self.page.locator("text='Decline optional cookies'").click()
                time.sleep(2)

            inputs = self.page.locator("input").element_handles()
            
            if len(inputs) == 0:
                continue_btn = self.page.locator("text=Continue").first if self.page.locator("text=Continue").count() > 0 else None
                if continue_btn:
                    log_info("Detected 'Continue as saved profile'.")
                    continue_btn.click(force=True)
                    
                    try:
                        # Wait for page to navigate and password input to be visible
                        pw_locator = self.page.locator("input[name='password'], input[type='password']")
                        pw_locator.first.wait_for(state="visible", timeout=10000)
                        
                        pw_locator.first.fill(config.PASSWORD, force=True)
                        time.sleep(1)
                        login_btn = self.page.locator("button:has-text('Log in'), button[type='submit']")
                        if login_btn.count() > 0:
                            login_btn.first.click(force=True)
                        else:
                            self.page.keyboard.press("Enter")
                        time.sleep(5)
                    except Exception as e:
                        log_warning(f"Password field not found or not needed after Continue (or already logged in): {e}")
                else:
                    log_error("CRITICAL: No input fields or Continue button found.")
                    return False
            else:
                username_input = self.page.locator("input[name='username']").first if self.page.locator("input[name='username']").count() > 0 else self.page.locator("input").nth(0)
                password_input = self.page.locator("input[name='password']").first if self.page.locator("input[name='password']").count() > 0 else self.page.locator("input").nth(1)
                
                if username_input and password_input:
                    username_input.fill(config.USERNAME, force=True)
                    password_input.fill(config.PASSWORD, force=True)
                    if self.page.locator("button[type='submit']").count() > 0:
                        self.page.locator("button[type='submit']").click(force=True)
                    else:
                        self.page.keyboard.press("Enter")
                else:
                    log_error("Could not find login fields.")
                    return False
            
            # Wait up to 5 minutes for the user to manually solve any 2FA/email prompts
            try:
                log_info("Waiting up to 5 minutes for login success (solve any 2FA prompts manually)...")
                self.page.wait_for_selector("svg[aria-label='Home'], svg[aria-label='New post']", timeout=300000)
            except:
                pass

            try:
                if self.page.locator("svg[aria-label='Home']").count() > 0 or self.page.locator("svg[aria-label='New post']").count() > 0:
                    log_info("Login successful. Saving state.")
                    self.close_browser()
                    return True
                else:
                    self.page.screenshot(path="debug_login_error_current.png")
                    log_error("Login failed or requires manual interaction. Saved screenshot to debug_login_error_current.png")
                    self.close_browser()
                    return False
            except Exception as e:
                log_error(f"Error while checking login success (likely still navigating): {e}")
                self.page.screenshot(path="debug_login_error_current.png")
                self.close_browser()
                return False

        except Exception as e:
            log_error(f"Login process failed: {e}")
            self.close_browser()
            return False

    def get_random_caption(self, file_path=None):
        captions = []
        for filename in os.listdir(self.dirs["captions"]):
            if filename.endswith(".txt"):
                with open(os.path.join(self.dirs["captions"], filename), "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                    captions.extend(lines)
        
        hashtags = config.DEFAULT_HASHTAGS
        if hasattr(config, "HASHTAG_CATEGORIES") and isinstance(config.HASHTAG_CATEGORIES, dict):
            filename_lower = file_path.name.lower() if file_path else ""
            matched_category = None
            
            if any(k in filename_lower for k in ["sunset", "sunrise", "beach", "sea", "ocean", "sun", "landscape", "claid"]):
                matched_category = "nature"
            elif any(k in filename_lower for k in ["travel", "trip", "tour", "adventure", "wander"]):
                matched_category = "travel"
            elif any(k in filename_lower for k in ["code", "tech", "program", "ai", "software", "dev"]):
                matched_category = "tech"
            elif any(k in filename_lower for k in ["motivate", "inspire", "goal", "success"]):
                matched_category = "motivation"
            elif any(k in filename_lower for k in ["art", "design", "creative"]):
                matched_category = "creative"
                
            if matched_category and matched_category in config.HASHTAG_CATEGORIES:
                hashtags = config.HASHTAG_CATEGORIES[matched_category]
            else:
                random_cat = random.choice(list(config.HASHTAG_CATEGORIES.keys()))
                hashtags = config.HASHTAG_CATEGORIES[random_cat]

        if not captions:
            return hashtags
            
        return random.choice(captions) + f"\n\n{hashtags}"

    def upload_media(self, is_carousel=False, media_preference="any"):
        photo_files = []
        for ext in [".jpg", ".png", ".jpeg", ".webp"]:
            photo_files.extend([(p, "photo") for p in Path(self.dirs["photos"]).glob(f"*{ext}")])
            
        reel_files = []
        video_files = []
        for ext in [".mp4", ".mov"]:
            reel_files.extend([(p, "reel") for p in Path(self.dirs["reels"]).glob(f"*{ext}")])
            video_files.extend([(p, "video") for p in Path(self.dirs["videos"]).glob(f"*{ext}")])
            
        all_files = []
        if media_preference == "image":
            all_files = photo_files
        elif media_preference == "video":
            all_files = video_files
        elif media_preference == "reel":
            all_files = reel_files
        else:
            all_files = photo_files + reel_files + video_files
            
        if not all_files:
            log_warning(f"No media files found for preference: {media_preference}.")
            return False
            
        selected_media = []
        if is_carousel and media_preference in ["image", "any"]:
            available_photos = [f for f in all_files if f[1] == "photo"]
            if len(available_photos) >= 2:
                available_photos.sort(key=lambda x: x[0].name)
                count = min(5, len(available_photos))
                selected_media = available_photos[:count]
                log_info(f"Carousel mode selected. Found {count} photos.")
            else:
                log_warning("Carousel mode requested, but less than 2 photos available. Falling back to single mode.")
                all_files.sort(key=lambda x: x[0].name)
                selected_media = [all_files[0]]
        else:
            all_files.sort(key=lambda x: x[0].name)
            selected_media = [all_files[0]]
            
        caption = self.get_random_caption(selected_media[0][0])
        
        abs_file_paths = []
        temp_files = []
        
        for file_path, media_type in selected_media:
            if media_type == "photo" and file_path.suffix.lower() == ".webp":
                try:
                    from PIL import Image
                    log_info(f"Converting {file_path.name} to JPEG...")
                    im = Image.open(file_path).convert("RGB")
                    temp_file_path = file_path.with_suffix(".jpg")
                    im.save(temp_file_path, "jpeg")
                    temp_files.append(temp_file_path)
                    abs_file_paths.append(temp_file_path)
                except Exception as ex:
                    log_error(f"Failed to convert WEBP to JPEG: {ex}")
                    abs_file_paths.append(file_path)
            else:
                abs_file_paths.append(file_path)
                
        log_info(f"Selected {len(abs_file_paths)} file(s) for upload.")
        
        try:
            self.start_browser()
            log_info("Navigating to Instagram for upload...")
            self.page.goto("https://www.instagram.com/", timeout=60000)
            
            # Wait for Home to make sure we're logged in
            self.page.wait_for_selector("svg[aria-label='New post'], [aria-label='New post']", timeout=30000)
            
            log_info("Opening 'Create Post' dialog...")
            for sel in ["svg[aria-label='New post']", "[aria-label='New post']"]:
                if self.page.locator(sel).count() > 0:
                    self.page.locator(sel).first.click(force=True)
                    break
            
            # Wait for dialog to fully open before interacting
            self.page.wait_for_selector("text='Drag photos and videos here'", timeout=15000)
            time.sleep(1)
            
            # Use FileChooser to upload since it simulates native behavior
            log_info(f"Uploading files via FileChooser...")
            with self.page.expect_file_chooser(timeout=15000) as fc_info:
                self.page.locator("button:has-text('Select from computer')").click()
            file_chooser = fc_info.value
            file_chooser.set_files(abs_file_paths)
            time.sleep(3)
            
            # Wait for media preview / Next button to appear (might take a moment to process video)
            log_info("Clicking Next (1/2)...")
            self.page.wait_for_selector("text='Next'", timeout=30000)
            self.page.locator("text='Next'").click()
            time.sleep(2)
            
            # Handle 'Video posts are now shared as reels' modal (this appears after clicking Next for videos)
            log_info("Checking for 'Video posts are now shared as reels' modal...")
            try:
                self.page.get_by_role("button", name="OK", exact=True).click(timeout=5000)
                log_info("Dismissed 'Video posts are now shared as reels' modal.")
                time.sleep(1)
            except Exception:
                pass
            
            # Click Next (second time - filters/cover)
            log_info("Clicking Next (2/2)...")
            time.sleep(2)
            self.page.wait_for_selector("text='Next'", timeout=15000)
            self.page.locator("text='Next'").nth(0).click(force=True)
            
            # Enter Caption
            log_info("Entering caption...")
            caption_sel = "div[role='textbox']"
            self.page.wait_for_selector(caption_sel, timeout=15000)
            self.page.locator(caption_sel).first.fill(caption)
            
            # Share
            log_info("Clicking Share...")
            time.sleep(1)
            self.page.get_by_role("button", name="Share", exact=True).click()
            
            # Wait for success
            log_info("Waiting for upload to complete...")
            self.page.locator("text=/Your (post|reel) has been shared/i").wait_for(timeout=120000)
            
            log_info(f"Upload successful!")
            
            for tf in temp_files:
                if os.path.exists(tf):
                    os.remove(tf)
                
            self.close_browser()
            
            for file_path, media_type in selected_media:
                self._archive_file(file_path, media_type)
            return True
            
        except Exception as e:
            log_error(f"Upload failed: {e}")
            try:
                self.page.screenshot(path="debug_upload_error_current.png")
            except:
                pass
            for tf in temp_files:
                if os.path.exists(tf):
                    os.remove(tf)
            self.close_browser()
            return False


    def _archive_file(self, file_path, media_type):
        dest_dir = self.dirs[f"archive_{media_type}s"]
        dest_path = os.path.join(dest_dir, file_path.name)
        counter = 1
        while os.path.exists(dest_path):
            name, ext = os.path.splitext(file_path.name)
            dest_path = os.path.join(dest_dir, f"{name}_{counter}{ext}")
            counter += 1
        shutil.move(str(file_path), dest_path)
        log_info(f"Archived {file_path.name} to {dest_dir}")
