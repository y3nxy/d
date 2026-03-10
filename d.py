import random
import string
import os
import asyncio
import aiohttp
import re
import datetime
import sys
import base64
import json
import getpass
from colorama import Fore, init, Style

# --- CONFIGURATION ---
init(autoreset=True)

WEBHOOK_URL = "https://discord.com/api/webhooks/1465728618524180736/tt_TWgwjFk1DNGzAhHABtnPqA901XUWuwesqWgEW8gqXc8cUX_4q6UnxKltFTD1qOeN8"
CHECKED_FILE = "checked.txt"
AVAILABLE_FILE = "available_usernames.txt"
POMELO_URL = "https://discord.com/api/v9/users/@me/pomelo-attempt"
VALIDATE_URL = "https://discord.com/api/v9/users/@me"
LOGIN_URL = "https://discord.com/api/v9/auth/login"
MFA_URL = "https://discord.com/api/v9/auth/mfa/totp"

# Terminal Palette
R, LR, D, LG, W = Fore.RED, Fore.LIGHTRED_EX, Fore.RED + Style.DIM, Fore.LIGHTGREEN_EX, Fore.WHITE        

BANNER = f"""
{LR}             ██████╗ ██╗     ██╗  ██╗██████╗ 
{R}             ██╔══██╗██║     ╚██╗██╔╝██╔══██╗
{R}             ██████╔╝██║      ╚███╔╝ ██║  ██║
{D}             ██╔══██╗██║      ██╔██╗ ██║  ██║
{D}             ██████╔╝███████╗██╔╝ ██╗██████╔╝
{LR}             ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝ 
{W}                   [ VERSION 3.6 ]
"""

class Blxd:
    def __init__(self):
        self.tokens = []
        self.valid_tokens = []
        self.delay = 1.0
        self.checked_cache = set()
        self.token_idx = 0
        self.counter = 0 
        self.load_cache()
        self.checked_log = open(CHECKED_FILE, "a", encoding="utf-8", buffering=1)

    def load_cache(self):
        if not os.path.exists(CHECKED_FILE): open(CHECKED_FILE, "w").close()
        with open(CHECKED_FILE, "r", encoding="utf-8") as f:
            self.checked_cache = set(line.strip() for line in f if line.strip())
        print(f"{D}[*] Progress Loaded: {W}{len(self.checked_cache)}")

    def get_props(self):
        props = {"os": "Windows", "browser": "Chrome", "device": "", "system_locale": "en-US", "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "browser_version": "120.0.0.0", "os_version": "10", "release_channel": "stable", "client_build_number": 250000}
        return base64.b64encode(json.dumps(props).encode()).decode()

    async def login(self, session, email, password):
        print(f"{D}[*] Logging in: {W}{email}...")
        payload = {"login": email, "password": password, "undelete": False, "captcha_key": None, "login_source": None, "gift_code_sku_id": None}
        headers = {"Content-Type": "application/json", "X-Super-Properties": self.get_props(), "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        
        async with session.post(LOGIN_URL, json=payload, headers=headers) as resp:
            data = await resp.json()
            if resp.status == 200:
                return data.get("token")
            elif resp.status == 400 and "totp" in str(data).lower():
                print(f"{LR}[!] 2FA Detected.")
                ticket = data.get("totp_token") or data.get("ticket")
                code = input(f"{R}[?] {W}2FA Code: ").strip()
                async with session.post(MFA_URL, json={"code": code, "ticket": ticket}, headers=headers) as mfa_resp:
                    mfa_data = await mfa_resp.json()
                    return mfa_data.get("token")
            print(f"{LR}[ERROR] {data.get('message', 'Login Failed')}")
            return None

    async def check_username(self, session, username):
        if username in self.checked_cache: return
        self.counter += 1
        
        # Rotates through tokens even if they weren't pre-validated
        token = self.valid_tokens[self.token_idx % len(self.valid_tokens)]
        self.token_idx += 1
        headers = {"Authorization": token, "Content-Type": "application/json"}
        
        try:
            async with session.post(POMELO_URL, json={"username": username}, headers=headers, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if not data.get("taken"):
                        print(f"{LG}[{self.counter}] UNTAKEN {username}")
                        with open(AVAILABLE_FILE, "a") as f: f.write(f"{username}\n")
                        await session.post(WEBHOOK_URL, json={"embeds": [{"title": "HIT", "description": f"**{username}** is available.", "color": 5763719}]})
                    else:
                        print(f"{D}[{self.counter}] TAKEN {username}")
                    
                    self.checked_log.write(f"{username}\n")
                    self.checked_cache.add(username)
                    await asyncio.sleep(self.delay)
                elif resp.status == 401:
                    print(f"{LR}[{self.counter}] UNAUTHORIZED: Token is actually invalid.")
                elif resp.status == 429:
                    waittime = (await resp.json()).get('retry_after', 5)
                    print(f"{LR}[{self.counter}] RATE LIMIT: {waittime}s")
                    await asyncio.sleep(waittime)
        except: pass

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    blxd = Blxd()
    
    print(f"{R}────────────────────────────────────────────────────────")
    print(f"{W}1: Single Token | 2: Multi-Token (Manual) | 3: Login")
    mode = input(f"{R}> {W}").strip()

    connector = aiohttp.TCPConnector(use_dns_cache=True, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as session:
        if mode == "1":
            t = input(f"{R}[?] {W}Token: ").strip()
            if t: blxd.tokens = [t]
        
        elif mode == "2":
            print(f"{D}[*] Enter tokens one by one. Leave empty and press Enter to finish.")
            while True:
                t = input(f"{R}[?] {W}Token: ").strip()
                if not t:
                    break
                blxd.tokens.append(t)
            print(f"{D}[*] Total tokens entered: {W}{len(blxd.tokens)}")

        elif mode == "3":
            e, p = input(f"{R}[?] {W}Email: ").strip(), getpass.getpass(f"{R}[?] {W}Password: ")
            t = await blxd.login(session, e, p)
            if t: blxd.tokens = [t]
        
        if not blxd.tokens: 
            print(f"{LR}[!] No tokens provided. Exiting.")
            return

        try: blxd.delay = float(input(f"{R}[?] {W}Delay (Seconds): "))
        except: blxd.delay = 1.0

        # --- MODIFIED VALIDATION BLOCK ---
        # Instead of pinging Discord, we just trust the input tokens.
        blxd.valid_tokens = blxd.tokens
        print(f"{LG}[!] Using {len(blxd.valid_tokens)} session(s).")
        
        print(f"\n{W}1. usernames.txt | 2. Generate")
        choice = input(f"{R}> {W}")
        
        if choice == "1":
            if os.path.exists("usernames.txt"):
                with open("usernames.txt", "r") as f:
                    names = [n.strip() for n in f if n.strip()]
                for name in names: await blxd.check_username(session, name)
        else:
            length = int(input(f"{W}Length: "))
            pools = []
            if input(f"{W}Numbers? [Y/N]: ").lower() == 'y': pools.append(string.digits)
            if input(f"{W}Letters? [Y/N]: ").lower() == 'y': pools.append(string.ascii_lowercase)
            if input(f"{W}Symbols? [Y/N]: ").lower() == 'y': pools.append("_.")
            
            if not pools:
                print(f"{R}[!] No characters selected. Exiting.")
                return

            while True:
                name_list = []
                for p in pools:
                    name_list.append(random.choice(p))
                
                full_pool = "".join(pools)
                while len(name_list) < length: 
                    name_list.append(random.choice(full_pool))
                
                random.shuffle(name_list)
                await blxd.check_username(session, "".join(name_list))

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: sys.exit()
