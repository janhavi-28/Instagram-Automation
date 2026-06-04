import schedule
import time
from logger import log_info, log_error
import config
from uploader import InstagramUploader

def job(is_carousel, media_preference):
    log_info("Starting scheduled upload job...")
    uploader = InstagramUploader()
    if uploader.login():
        uploader.upload_media(is_carousel=is_carousel, media_preference=media_preference)
    else:
        log_error("Skipping upload due to login failure.")

def run_scheduler(is_carousel=False, media_preference="any"):
    interval = config.POST_INTERVAL_MINUTES
    log_info(f"Scheduler started. Next upload in exactly {interval} minutes.")
    
    # Schedule the job
    schedule.every(interval).minutes.do(job, is_carousel=is_carousel, media_preference=media_preference)
    
    # Run once immediately on start
    job(is_carousel, media_preference)
    
    while True:
        schedule.run_pending()
        time.sleep(60) # check every minute
