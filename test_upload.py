"""
Test: inject video as base64 directly into JS, build a real File/DataTransfer,
and dispatch a drop event on Instagram's dialog.
No network fetch needed — bypasses CSP entirely.
Run: python test_upload.py
"""
import os, time, base64
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION = "sessions/state.json"
VIDEO   = Path("reels/3256768-uhd_2160_3840_25fps.mp4").absolute()

DROP_JS = """
async ([b64, filename]) => {
    // 1. Decode base64 -> Uint8Array -> Blob -> File
    const binary = atob(b64);
    const bytes  = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    const blob = new Blob([bytes], { type: 'video/mp4' });
    const file = new File([blob], filename, { type: 'video/mp4' });

    // 2. Build DataTransfer
    const dt = new DataTransfer();
    dt.items.add(file);

    // 3. Find the drop zone inside the dialog
    const zone = document.querySelector("div[role='dialog']")
              || document.body;

    // 4. Fire drag events on the drop zone
    for (const type of ['dragenter', 'dragover', 'drop']) {
        zone.dispatchEvent(new DragEvent(type, {
            bubbles: true, cancelable: true, dataTransfer: dt
        }));
        await new Promise(r => setTimeout(r, 150));
    }

    // 5. Also fire change on the file input, in case Instagram listens there too
    const inp = document.querySelector("input[type='file']");
    if (inp) {
        // Try to override the files property
        try {
            Object.defineProperty(inp, 'files', { value: dt.files, configurable: true });
        } catch(e) {}
        inp.dispatchEvent(new Event('change', { bubbles: true }));
        inp.dispatchEvent(new Event('input',  { bubbles: true }));
    }

    return { ok: true, fileName: file.name, sizeKB: Math.round(file.size/1024) };
}
"""

def run():
    print(f"[0] Reading video file ({VIDEO.stat().st_size // 1024 // 1024} MB)...")
    raw   = VIDEO.read_bytes()
    b64   = base64.b64encode(raw).decode("ascii")
    print(f"    base64 length: {len(b64):,} chars")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        ctx = browser.new_context(
            storage_state=SESSION if os.path.exists(SESSION) else None,
            locale="en-US",
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.new_page()

        print("[1] Navigating to Instagram...")
        page.goto("https://www.instagram.com/", timeout=60000)
        time.sleep(4)
        print(f"    URL: {page.url}")

        print("[2] Clicking Create/New post...")
        for sel in ["svg[aria-label='New post']", "[aria-label='New post']"]:
            if page.locator(sel).count() > 0:
                page.locator(sel).first.click(force=True)
                print(f"    Clicked: {sel}")
                break
        time.sleep(3)
        page.screenshot(path="test_02_dialog.png")

        print("[3] Injecting video bytes via DataTransfer drop event (JS)...")
        result = page.evaluate(DROP_JS, [b64, VIDEO.name])
        print(f"    JS result: {result}")

        print("[4] Waiting 45s to see if video loads into Instagram dialog...")
        for i in range(9):
            time.sleep(5)
            video_count  = page.locator("video").count()
            next_count   = page.locator("button:has-text('Next')").count()
            drag_visible = page.locator("text=Drag photos and videos here").count()
            print(f"    t+{(i+1)*5}s: video={video_count}, Next={next_count}, drag_screen={drag_visible}")
            page.screenshot(path=f"test_04_wait_{i}.png")
            if video_count > 0 or next_count > 0:
                print("    [OK] VIDEO LOADED! DataTransfer+base64 approach WORKS!")
                break
        else:
            print("    [FAIL] Video did NOT load after 45s")
            print("    Check test_04_wait_*.png screenshots")

        ctx.storage_state(path=SESSION)
        browser.close()

if __name__ == "__main__":
    run()
