# Instagram Automation Bot

A fully automated Instagram bot to schedule and upload photos, reels, and videos using Python and Instagrapi, complete with a Streamlit dashboard.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Open `config.py` and add your Instagram `USERNAME` and `PASSWORD`. You can also configure scheduling intervals and default hashtags.
3. Add your media:
   - Place `.jpg` or `.png` files in the `photos/` directory.
   - Place `.mp4` files in the `reels/` directory.
   - Place `.mp4` or `.mov` files in the `videos/` directory.
4. Add your captions:
   - Place `.txt` files in the `captions/` directory. Each line in a `.txt` file will be treated as a separate caption (blank lines are ignored). The bot randomly selects a caption.

## Usage

### Run the Bot Scheduler
To run the bot in the background (will check and upload every X hours defined in `config.py`):
```bash
python main.py
```

### Run an Immediate Upload
To force an upload right now without waiting:
```bash
python main.py --now
```

### Run the Dashboard
To see upload stats and logs:
```bash
streamlit run dashboard.py
```
