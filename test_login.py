from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.instagram.com/")
        time.sleep(5)
        
        # print all inputs
        inputs = page.locator("input").element_handles()
        print(f"Found {len(inputs)} inputs")
        for i in inputs:
            print("INPUT:")
            print("  name:", i.get_attribute("name"))
            print("  type:", i.get_attribute("type"))
            print("  aria-label:", i.get_attribute("aria-label"))
            
        print("Done")
        browser.close()

if __name__ == "__main__":
    run()
