import json
import os
from instagrapi import Client

def test():
    # 1. Read sessionid from Playwright state
    state_file = 'sessions/state.json'
    if not os.path.exists(state_file):
        print("No Playwright state file found.")
        return
        
    with open(state_file, 'r') as f:
        cookies = json.load(f).get('cookies', [])
        
    sessionid = next((c['value'] for c in cookies if c['name'] == 'sessionid'), None)
    if not sessionid:
        print("No sessionid cookie found.")
        return
        
    print(f"Found sessionid: {sessionid[:10]}...")
    
    # 2. Login via instagrapi
    cl = Client()
    cl.login_by_sessionid(sessionid)
    print("Instagrapi logged in via sessionid!")
    
    # 3. Test profile fetch
    user = cl.user_info_by_username("instagram")
    print(f"Test fetch instagram profile: {user.full_name}")

if __name__ == "__main__":
    test()
