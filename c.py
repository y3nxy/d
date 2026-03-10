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
AVAILABLE_FILE = "available_usernames.txt"

# API Endpoints
POMELO_URL = "https://discord.com/api/v9/users/@me/pomelo-attempt"
ROBLOX_URL = "https://auth.roblox.com/v1/usernames/validate"

# Terminal Palette
R, LR, D, LG, W = Fore.RED, Fore.LIGHTRED_EX, Fore.RED + Style.DIM, Fore.LIGHTGREEN_EX, Fore.WHITE        

BANNER = f"""
{LR}             ██████╗ ██╗     ██╗  ██╗██████╗ 
{R}             ██╔══██╗██║     ╚██╗██╔╝██╔══██╗
{R}             ██████╔╝██║      ╚███╔╝ ██║  ██║
{D}             ██╔══██╗██║      ██╔██╗ ██║  ██║
{D}             ██████╔╝███████╗██╔╝ ██╗██████╔╝
{LR}             ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝ 
{W}               [ MULTI-THREADED CHECKER ]
"""

class UnifiedChecker:
    def __init__(self, threads):
        self.semaphore = asyncio.Semaphore(threads) # The "Bouncer" for threads
        self.checked_cache = set()
        self.counter = 0
        self.load_cache()

    def load_cache(self):
        if not os.path.exists(CHECKED_FILE): open(CHECKED_FILE, "w").close()
        with open(CHECKED_FILE, "r", encoding="utf-8") as f:
            self.checked_cache = set(line.strip() for line in f if line.strip())

    def kill_process(self, platform):
        """Forces the script to shut down instantly."""
        print(f"\n{LR}[!!!] CRITICAL RATE LIMIT ON {platform.upper()}")
        print(f"{R}Shutting down to prevent IP/Account flag...")
        os._exit(0) # Immediate exit, skips all cleanup

    async def discord_check(self, session, token, username):
        async with self.semaphore:
            if username in self.checked_cache: return
            headers = {"Authorization": token, "Content-Type": "application/json"}
            try:
                async with session.post(POMELO_URL, json={"username": username}, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.counter += 1
                        if not data.get("taken"):
                            print(f"{LG}[{self.counter}] DISCORD: {username}")
                            with open(AVAILABLE_FILE, "a") as f: f.write(f"Discord: {username}\n")
                        else:
                            print(f"{D}[{self.counter}] TAKEN: {username}")
                        self.checked_cache.add(username)
                    elif resp.status == 429:
                        self.kill_process("Discord")
            except Exception: pass

    async def roblox_check(self, session, username):
        async with self.semaphore:
            if username in self.checked_cache: return
            params = {"username": username, "birthday": "2000-01-01", "context": "Signup"}
            try:
                async with session.get(ROBLOX_URL, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.counter += 1
                        if data.get("code") == 0:
                            print(f"{LG}[{self.counter}] ROBLOX: {username}")
                            with open(AVAILABLE_FILE, "a") as f: f.write(f"Roblox: {username}\n")
                        else:
                            print(f"{D}[{self.counter}] TAKEN: {username}")
                        self.checked_cache.add(username)
                    elif resp.status == 429:
                        self.kill_process("Roblox")
            except Exception: pass

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    
    print(f"{W}1. Discord | 2. Roblox")
    platform = input(f"{R}> {W}").strip()
    
    threads = int(input(f"{W}Threads (Recommended 5-10): "))
    length = int(input(f"{W}Username Length: "))
    
    token = ""
    if platform == "1":
        token = input(f"{R}[?] {W}Discord Token: ").strip()

    checker = UnifiedChecker(threads)
    
    async with aiohttp.ClientSession() as session:
        print(f"{R}────────────────────────────────────────────────────────")
        while True:
            # Create a batch of tasks to run concurrently
            pool = string.ascii_lowercase + string.digits + "_"
            tasks = []
            
            for _ in range(threads * 2): # Buffer tasks
                name = ''.join(random.choice(pool) for _ in range(length))
                if platform == "1":
                    tasks.append(checker.discord_check(session, token, name))
                else:
                    tasks.append(checker.roblox_check(session, name))
            
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.1) # Tiny breather between batches

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        os._exit(0)