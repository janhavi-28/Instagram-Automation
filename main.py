import argparse
from uploader import InstagramUploader
from scheduler import run_scheduler
from logger import log_info, log_error

def main():
    parser = argparse.ArgumentParser(description="Instagram Automation Bot")
    parser.add_argument("--now", action="store_true", help="Run upload immediately instead of starting scheduler")
    
    args = parser.parse_args()
    
    log_info("Initializing Instagram Automation Bot...")
    
    media_type = input("What do you want to upload? (image/video/reel/any) [default: any]: ").strip().lower()
    if media_type in ["images", "image"]:
        media_type = "image"
    elif media_type in ["videos", "video"]:
        media_type = "video"
    elif media_type in ["reels", "reel"]:
        media_type = "reel"
    else:
        media_type = "any"
        
    is_carousel = False
    if media_type in ["image", "any"]:
        mode = input("Do you want to upload a carousel of images or a single file? (carousel/single) [default: single]: ").strip().lower()
        is_carousel = (mode == 'carousel')

    if args.now:
        log_info("Running upload job immediately.")
        uploader = InstagramUploader()
        if uploader.login():
            uploader.upload_media(is_carousel=is_carousel, media_preference=media_type)
        else:
            log_error("Login failed. Check your config.py credentials.")
    else:
        # Default behavior: run scheduler
        run_scheduler(is_carousel=is_carousel, media_preference=media_type)

if __name__ == "__main__":
    main()
