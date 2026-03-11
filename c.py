import random
import string
import os
import asyncio
import aiohttp
import sys
from colorama import Fore, init, Style

# --- CONFIGURATION ---
init(autoreset=True)

CHECKED_FILE = "checked.txt"
AVAILABLE_FILE = "available.txt"

# API Endpoints
POMELO_URL = "https://discord.com/api/v9/users/@me/pomelo-attempt"
ROBLOX_URL = "https://auth.roblox.com/v1/usernames/validate"
GITHUB_URL = "https://api.github.com/users/"
YOUTUBE_URL = "https://www.youtube.com/@"
TIKTOK_URL = "https://www.tiktok.com/@"
TWITCH_URL = "https://passport.twitch.tv/usernames/"
INSTA_URL = "https://www.instagram.com/"

# Colors
R, LR, D, LG, W = Fore.RED, Fore.LIGHTRED_EX, Fore.RED + Style.DIM, Fore.LIGHTGREEN_EX, Fore.WHITE        

BANNER = f"""
{LR}             ██████╗ ██╗     ██╗  ██╗██████╗ 
{R}             ██╔══██╗██║     ╚██╗██╔╝██╔══██╗
{R}             ██████╔╝██║      ╚███╔╝ ██║  ██║
{D}             ██╔══██╗██║      ██╔██╗ ██║  ██║
{D}             ██████╔╝███████╗██╔╝ ██╗██████╔╝
{LR}             ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝ 
{W}                    MADE BY Y3NXY
{D}                [ V5.4 - FINAL STABLE ]
"""

class MultiChecker:
    def __init__(self, threads, delay):
        self.semaphore = asyncio.Semaphore(threads)
        self.delay = delay
        self.checked_cache = set()
        self.counter = 0
        self.load_cache()

    def load_cache(self):
        if not os.path.exists(CHECKED_FILE): open(CHECKED_FILE, "w").close()
        with open(CHECKED_FILE, "r", encoding="utf-8") as f:
            self.checked_cache = set(line.strip() for line in f if line.strip())

    def kill_switch(self, platform, reason="Rate Limit"):
        print(f"\n{LR}[!!!] {platform.upper()} EMERGENCY STOP: {reason}")
        print(f"{R}Stopping this session to protect your IP...{W}\n")
        os._exit(0) 

    async def log_status(self, platform, username, available):
        self.counter += 1
        label = f"[{platform.upper()}]"
        if available:
            print(f"{W}{label} {username}: {LG}UNTAKEN")
            with open(AVAILABLE_FILE, "a") as f: f.write(f"{platform}: {username}\n")
        else:
            print(f"{W}{label} {username}: {D}TAKEN")
        self.checked_cache.add(username)

    async def check_generic(self, session, platform, url, username):
        async with self.semaphore:
            if username in self.checked_cache: return
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Accept": "application/vnd.github+json" if platform == "GitHub" else "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            try:
                await asyncio.sleep(self.delay)
                async with session.get(f"{url}{username}", headers=headers, timeout=10, allow_redirects=False) as resp:
                    if resp.status == 429 or (platform == "GitHub" and resp.status == 403):
                        self.kill_switch(platform)
                    
                    if resp.status in [301, 302]:
                        loc = resp.headers.get('Location', '')
                        if "login" in loc or "challenge" in loc:
                            self.kill_switch(platform, "Bot Detection Redirect")
                        else:
                            await self.log_status(platform, username, False)
                    elif resp.status == 404:
                        await self.log_status(platform, username, True)
                    else:
                        await self.log_status(platform, username, False)
            except: pass

    async def roblox_check(self, session, username):
        async with self.semaphore:
            if username in self.checked_cache: return
            params = {"username": username, "birthday": "2000-01-01", "context": "Signup"}
            try:
                await asyncio.sleep(self.delay)
                async with session.get(ROBLOX_URL, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        await self.log_status("Roblox", username, data.get("code") == 0)
                    elif resp.status == 429: self.kill_switch("Roblox")
            except: pass

    async def discord_check(self, session, token, username):
        async with self.semaphore:
            if username in self.checked_cache: return
            headers = {"Authorization": token, "Content-Type": "application/json"}
            try:
                await asyncio.sleep(self.delay)
                async with session.post(POMELO_URL, json={"username": username}, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        await self.log_status("Discord", username, not data.get("taken"))
                    elif resp.status == 429: self.kill_switch("Discord")
            except: pass

def get_safe_name(length, pool):
    name = ''.join(random.choice(pool) for _ in range(length))
    if name[0] in "._-" or name[-1] in "._-":
        return get_safe_name(length, pool)
    return name

async def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        
        platforms = {"1":"Discord","2":"Roblox","3":"GitHub","4":"YouTube","5":"TikTok","6":"Twitch","7":"Instagram"}
        for k, v in platforms.items(): print(f"{R}{k}: {W}{v}", end="  ")
        
        try:
            print(f"\n\n{D}(Press Ctrl+C to Exit Script)")
            choice = input(f"{R}> {W}").strip()
        except KeyboardInterrupt:
            os._exit(0)

        if choice not in platforms: continue

        try:
            threads = int(input(f"{W}Threads: "))
            delay = float(input(f"{W}Delay: "))
            length = int(input(f"{W}Length: "))
            token = input(f"{R}[?] {W}Token (DC): ") if choice == "1" else ""
        except KeyboardInterrupt: continue 

        checker = MultiChecker(threads, delay)
        connector = aiohttp.TCPConnector(limit=threads, ssl=False)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            print(f"{R}────────────────────────────────────────────────────────")
            
            # Platform Specific Pools
            if choice == "3": pool = string.ascii_lowercase + string.digits + "-"
            elif choice == "7": pool = string.ascii_lowercase + string.digits + "._"
            elif choice == "4": pool = string.ascii_lowercase + string.digits + ".-"
            else: pool = string.ascii_lowercase + string.digits + "_"

            try:
                while True:
                    tasks = []
                    for _ in range(threads): 
                        name = get_safe_name(length, pool)
                        if choice == "1": tasks.append(checker.discord_check(session, token, name))
                        elif choice == "2": tasks.append(checker.roblox_check(session, name))
                        else:
                            p_name = platforms[choice]
                            url = globals()[f"{p_name.upper()}_URL"]
                            tasks.append(checker.check_generic(session, p_name, url, name))
                    await asyncio.gather(*tasks)
            except KeyboardInterrupt:
                print(f"\n{LR}[!] Stopping... Returning to menu.{W}")
                await asyncio.sleep(1)
                continue

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)