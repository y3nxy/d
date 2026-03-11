import random
import string
import os
import asyncio
import aiohttp
from colorama import Fore, init, Style

init(autoreset=True)

# --- PLATFORM DATABASE ---
# Format: "ID": (Name, URL, MinLength, MaxLength, AllowsUpper, SymbolsAllowed)
PLATFORMS = {
    "1": ("Discord", "https://discord.com/api/v9/users/@me/pomelo-attempt", 2, 32, False, "._"),
    "2": ("Roblox", "https://auth.roblox.com/v1/usernames/validate", 3, 20, True, "_"),
    "3": ("GitHub", "https://api.github.com/users/", 4, 39, True, "-"),
    "4": ("YouTube", "https://www.youtube.com/@", 3, 30, False, "._-"),
    "5": ("TikTok", "https://www.tiktok.com/@", 2, 24, True, "._"),
    "6": ("Twitch", "https://passport.twitch.tv/usernames/", 4, 25, True, "_"),
    "7": ("Instagram", "https://www.instagram.com/", 1, 30, True, "._")
}

R, LR, LG, W = Fore.RED, Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, Fore.WHITE

def get_safe_name(length, pool):
    name = ''.join(random.choice(pool) for _ in range(length))
    if name[0] in "._-" or name[-1] in "._-": # Can't start/end with symbols
        return get_safe_name(length, pool)
    return name

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{LR}=== MULTI-PLATFORM USERNAME CHECKER ===")
    
    for k, v in PLATFORMS.items():
        print(f"{R}{k}: {W}{v[0]}", end="  ")
    
    choice = input(f"\n\n{R}> {W}").strip()
    if choice not in PLATFORMS: return
    
    name, url, min_l, max_l, allows_up, symbols = PLATFORMS[choice]

    # 1. LENGTH CHECK
    while True:
        length = int(input(f"{W}Pick Length (Min {min_l} for {name}): "))
        if length < min_l:
            print(f"{R}[!] Error: {name} requires at least {min_l} characters.")
        elif length > max_l:
            print(f"{R}[!] Error: {name} max length is {max_l}.")
        else:
            break

    # 2. DELAY & THREADS
    threads = int(input(f"{W}Threads: "))
    delay = float(input(f"{W}Delay (e.g. 0.5): "))

    # 3. CHARACTER POOL SELECTION
    pool = ""
    if input(f"{W}Use Letters? (y/n): ").lower() == 'y':
        pool += string.ascii_lowercase
        if allows_up:
            if input(f"{W}Use Uppercase? (y/n): ").lower() == 'y':
                pool += string.ascii_uppercase
        else:
            print(f"{R}[!] Note: {name} is lowercase only. Skipping uppercase prompt.")

    if input(f"{W}Use Numbers? (y/n): ").lower() == 'y':
        pool += string.digits
    
    if input(f"{W}Use Symbols ({symbols})? (y/n): ").lower() == 'y':
        pool += symbols

    if not pool:
        print(f"{R}Error: No characters selected!")
        return

    # 4. RUN CHECKER (Logic remains the same as your original script)
    print(f"\n{LG}[*] Starting {name} check with {length} chars...")
    # ... rest of your aiohttp logic goes here ...

if __name__ == "__main__":
    asyncio.run(main())
