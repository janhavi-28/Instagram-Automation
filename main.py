import argparse
from uploader import InstagramUploader
from scheduler import run_scheduler
from logger import log_info, log_error

def main():
    parser = argparse.ArgumentParser(description="Instagram Automation Bot")
    parser.add_argument("--now", action="store_true", help="Run upload immediately instead of starting scheduler")
    
    args = parser.parse_args()
    
    log_info("Initializing Instagram Automation Bot...")
    
    if args.now:
        log_info("Running single upload job immediately.")
        uploader = InstagramUploader()
        if uploader.login():
            uploader.upload_media()
        else:
            log_error("Login failed. Check your config.py credentials.")
    else:
        # Default behavior: run scheduler
        run_scheduler()

if __name__ == "__main__":
    main()
