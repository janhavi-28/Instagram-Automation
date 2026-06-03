import asyncio
from playwright.async_api import async_playwright
import os
from pathlib import Path

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=False)
        context = await browser.new_context(storage_state="sessions/state.json")
        page = await context.new_page()
        
        await page.goto("https://www.instagram.com/")
        await page.wait_for_selector("svg[aria-label='New post']", timeout=30000)
        
        print("Clicking New Post...")
        await page.locator("svg[aria-label='New post']").first.click()
        
        print("Waiting for dialog...")
        await page.wait_for_selector("text='Drag photos and videos here'", timeout=10000)
        
        print("Testing file input...")
        # Get absolute path of first video
        media_dir = Path("videos")
        videos = list(media_dir.glob("*.mp4"))
        if not videos:
            print("No video found for testing!")
            return
            
        video_path = os.path.abspath(videos[0])
        print(f"Found video: {video_path}")
        
        try:
            print("1. Trying set_input_files on hidden input...")
            file_input = page.locator("input[type='file']")
            await file_input.set_input_files(video_path)
            
            # See if "Next" appears within 5 seconds
            try:
                await page.wait_for_selector("text='Next'", timeout=5000)
                print("SUCCESS: Method 1 (set_input_files) worked!")
                await browser.close()
                return
            except Exception:
                print("Method 1 failed. Upload UI didn't advance.")
        except Exception as e:
            print(f"Method 1 threw error: {e}")
            
        print("Testing file input with FileChooser...")
        try:
            async with page.expect_file_chooser(timeout=5000) as fc_info:
                await page.locator("button:has-text('Select from computer')").click()
            file_chooser = await fc_info.value
            await file_chooser.set_files(video_path)
            
            try:
                await page.wait_for_selector("text='Next'", timeout=15000)
                print("SUCCESS: Method 2 (filechooser) worked!")
                await browser.close()
                return
            except Exception:
                print("Method 2 failed. Upload UI didn't advance. Taking screenshot...")
                await page.screenshot(path="debug_video_reject.png")
        except Exception as e:
            print(f"Method 2 threw error: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
