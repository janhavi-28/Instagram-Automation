import streamlit as st
import os
import re

st.set_page_config(page_title="Instagram Bot Dashboard", layout="wide")

def count_files(directory, extensions):
    count = 0
    if os.path.exists(directory):
        for f in os.listdir(directory):
            if any(f.lower().endswith(ext) for ext in extensions):
                count += 1
    return count

def get_last_upload():
    log_file = "logs/uploads.log"
    last_upload = "Never"
    recent_logs = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            lines = f.readlines()
            
        recent_logs = lines[-10:] if len(lines) > 10 else lines
        
        for line in reversed(lines):
            if "Successfully uploaded" in line:
                match = re.search(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if match:
                    last_upload = match.group(1)
                    break
    return last_upload, recent_logs

st.title("🤖 Instagram Automation Bot Dashboard")

# Metrics
st.header("Status")
last_upload_time, logs = get_last_upload()
st.metric("Last Upload Time", last_upload_time)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Pending Media")
    pending_photos = count_files("photos", [".jpg", ".jpeg", ".png"])
    pending_reels = count_files("reels", [".mp4", ".mov"])
    pending_videos = count_files("videos", [".mp4", ".mov"])
    
    st.metric("Photos to Upload", pending_photos)
    st.metric("Reels to Upload", pending_reels)
    st.metric("Videos to Upload", pending_videos)

with col2:
    st.subheader("Archived (Uploaded)")
    archived_photos = count_files("archive/photos", [".jpg", ".jpeg", ".png"])
    archived_reels = count_files("archive/reels", [".mp4", ".mov"])
    archived_videos = count_files("archive/videos", [".mp4", ".mov"])
    
    st.metric("Total Uploaded Photos", archived_photos)
    st.metric("Total Uploaded Reels", archived_reels)
    st.metric("Total Uploaded Videos", archived_videos)

st.header("Recent Logs")
st.text_area("Last 10 Log Entries", value="".join(logs), height=200, disabled=True)
