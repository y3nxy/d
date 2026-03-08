import random
import string
import os
import asyncio
import aiohttp
from colorama import Fore, init, Style
import datetime
import sys

# --- CONFIGURATION & INITIALIZATION ---
init(autoreset=True)

# Hardcoded Webhook
WEBHOOK_URL = "https://discord.com/api/webhooks/1465728618524180736/tt_TWgwjFk1DNGzAhHABtnPqA901XUWuwesqWgEW8gqXc8cUX_4q6UnxKltFTD1qOeN8"
CHECKED_FILE = "checked.txt"
AVAILABLE_FILE = "available_usernames.txt"
POMELO_URL = "https://discord.com/api/v9/users/@me/pomelo-attempt"
VALIDATE_URL = "https://discord.com/api/v9/users/@me"

# Terminal Palette
R = Fore.RED          
LR = Fore.LIGHTRED_EX  
D = Fore.RED + Style.DIM 
G = Fore.GREEN
LG = Fore.LIGHTGREEN_EX
W = Fore.WHITE        
RESET = Style.RESET_ALL

BANNER = f"""
{LR}             ██████╗ ██╗     ██╗  ██╗██████╗ 
{R}             ██╔══██╗██║     ╚██╗██╔╝██╔══██╗
{R}             ██████╔╝██║      ╚███╔╝ ██║  ██║
{D}             ██╔══██╗██║      ██╔██╗ ██║  ██║
{D}             ██████╔╝███████╗██╔╝ ██╗██████╔╝
{LR}             ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝ 
{W}                   [ VERSION 2.4 ]
"""

class Blxd:
    def __init__(self):
        self.tokens = []
        self.valid_tokens = []
        self.delay = 1.0
        self.checked_cache = set()
        self.token_idx = 0
        self.load_cache()
        self.checked_log = open(CHECKED_FILE, "a", encoding="utf-8", buffering=1)

    def load_cache(self):
        if not os.path.exists(CHECKED_FILE):
            open(CHECKED_FILE, "w").close()
        with open(CHECKED_FILE, "r", encoding="utf-8") as f:
            self.checked_cache = set(line.strip() for line in f if line.strip())
        print(f"{D}[{W}* {D}] Progress Loaded: {W}{len(self.checked_cache)}")

    async def validate_all_tokens(self, session):
        print(f"{R}[{W}!{R}] {W}Checking Tokens...")
        tasks = [self.check_single_token(session, t) for t in self.tokens]
        results = await asyncio.gather(*tasks)
        self.valid_tokens = [t for t in results if t is not None]
        
        if not self.valid_tokens:
            print(f"{LR}[ERROR] No tokens work. Closing.")
            sys.exit()
        print(f"{LR}[OK] {W}{len(self.valid_tokens)} {LR}Tokens are ready.")

    async def check_single_token(self, session, token):
        headers = {"Authorization": token}
        try:
            async with session.get(VALIDATE_URL, headers=headers, timeout=5) as resp:
                if resp.status == 200:
                    user_data = await resp.json()
                    print(f"{D}#{LR} {W}{user_data.get('username')}")
                    return token
                return None
        except:
            return None

    def save_checked(self, username):
        if username not in self.checked_cache:
            self.checked_log.write(f"{username}\n")
            self.checked_cache.add(username)

    def log_available(self, username):
        with open(AVAILABLE_FILE, "a", encoding="utf-8") as f:
            f.write(f"{username}\n")

    def get_next_token(self):
        if not self.valid_tokens: return None
        token = self.valid_tokens[self.token_idx % len(self.valid_tokens)]
        self.token_idx += 1
        return token

    async def send_hit_webhook(self, session, username):
        payload = {
            "embeds": [{
                "title": "🎯 UNTAKEN USERNAME FOUND",
                "description": f"The username **{username}** is available.",
                "color": 5763719,
                "footer": {"text": "BLXD MONITORING"},
                "timestamp": str(datetime.datetime.utcnow())
            }]
        }
        try: await session.post(WEBHOOK_URL, json=payload, timeout=5)
        except: pass

    async def check_username(self, session, username):
        if username in self.checked_cache: return True
        token = self.get_next_token()
        if not token: return False

        headers = {"Authorization": token, "Content-Type": "application/json"}
        try:
            async with session.post(POMELO_URL, json={"username": username}, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("taken") is False and not data.get("errors"):
                        print(f"{LG}UNTAKEN {W}{username}")
                        self.log_available(username)
                        asyncio.create_task(self.send_hit_webhook(session, username))
                    else:
                        print(f"{D}TAKEN {username}")
                    
                    self.save_checked(username)
                    await asyncio.sleep(self.delay)
                    return True
                elif resp.status == 429:
                    print(f"\n{LR}RATE LIMITED. STOPPING.")
                    return False 
                elif resp.status == 401:
                    if token in self.valid_tokens: self.valid_tokens.remove(token)
                    return True 
                else:
                    self.save_checked(username)
                    return True
        except: return True

    async def run_list(self, session, filename):
        if not os.path.exists(filename): return
        with open(filename, "r") as f:
            names = [line.strip() for line in f if line.strip()]
        for name in names:
            if not await self.check_username(session, name): sys.exit() 

    async def run_gen(self, session, length, chars):
        while True:
            name = ''.join(random.choice(chars) for _ in range(length))
            if not await self.check_username(session, name): sys.exit()

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    blxd = Blxd()
    
    print(f"{R}────────────────────────────────────────────────────────")
    auth_mode = input(f"{W}1: One Token | 2: Token File\n{R}> {W}")
    if auth_mode == "1":
        t = input(f"{R}[?] {W}Token: ").strip()
        if t: blxd.tokens = [t]
    else:
        file = input(f"{R}[?] {W}File: ")
        if os.path.exists(file):
            with open(file, "r") as f: blxd.tokens = [l.strip() for l in f if l.strip()]
    
    if not blxd.tokens: return
    try: blxd.delay = float(input(f"{R}[?] {W}Delay: "))
    except: blxd.delay = 1.0

    async with aiohttp.ClientSession() as session:
        await blxd.validate_all_tokens(session)

        print(f"\n{W}1. Use usernames.txt")
        print(f"{W}2. Generate Names")
        main_choice = input(f"{R}> {W}")

        if main_choice == "1":
            await blxd.run_list(session, "usernames.txt")
        else:
            try:
                length = int(input(f"{W}How many characters? {R}> {W}"))
                pool = ""
                if input(f"{W}use numbers? [Y/N] {R}> {W}").lower() == 'y': pool += string.digits
                if input(f"{W}use letters? [Y/N] {R}> {W}").lower() == 'y': pool += string.ascii_lowercase
                if input(f"{W}use symbols? [Y/N] {R}> {W}").lower() == 'y': pool += "_."
                
                if not pool:
                    print(f"{LR}No characters selected.")
                    return
                await blxd.run_gen(session, length, pool)
            except ValueError:
                return

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: sys.exit()