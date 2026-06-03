import schedule
import time
from logger import log_info, log_error
import config
from uploader import InstagramUploader

def job():
    log_info("Starting scheduled upload job...")
    uploader = InstagramUploader()
    if uploader.login():
        uploader.upload_media()
    else:
        log_error("Skipping upload due to login failure.")

def run_scheduler():
    interval = config.POST_INTERVAL_HOURS
    log_info(f"Scheduler started. Next upload in {interval} hours.")
    
    # Schedule the job
    schedule.every(interval).hours.do(job)
    
    # Run once immediately on start (optional, uncomment if desired)
    # job()
    
    while True:
        schedule.run_pending()
        time.sleep(60) # check every minute
