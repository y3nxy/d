import random
import string 
import requests
import os
import time
import sys
from colorama import Fore, init, Style

init(autoreset=True)

# --- CONFIG & GLOBALS ---
VERSION = "3.2"
URL = "https://discord.com/api/v9/users/@me/pomelo-attempt"
SYS_URL = "https://discord.com/api/v9/users/@me"
checked_usernames = set()  # Ensures no duplicates during session
av_list = "available_usernames.txt"
tokens = []
current_token_index = 0

# --- COLOR PALETTE ---
R1 = "\033[38;2;255;0;0m"     # Pure Red
R2 = "\033[38;2;200;0;0m"     # Mid Red
R3 = "\033[38;2;150;0;0m"     # Dark Red
R4 = "\033[38;2;100;0;0m"     # Deep Red
W = Fore.WHITE
G = Fore.LIGHTBLACK_EX
RESET = Style.RESET_ALL

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def fade_logo():
    # Fading gradient effect for BLXD
    print(f"""
{R1}             ██████╗ ██╗      ██╗  ██╗██████╗ 
{R2}             ██╔══██╗██║      ╚██╗██╔╝██╔══██╗
{R3}             ██████╔╝██║       ╚███╔╝ ██║  ██║
{R4}             ██╔══██╗██║       ██╔██╗ ██║  ██║
{R4}             ██████╔╝███████╗██╔╝ ██╗██████╔╝ 
{R4}             ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝  
                    {W}[ VERSION {VERSION} ]
    """)

def get_input(prompt, color=W):
    return input(f"{G}[{R1}?{G}] {color}{prompt}{R1}: {W}")

def setup():
    global tokens, current_token_index
    clear()
    fade_logo()
    
    print(f"{R1}1. {W}single token?    {R1}2. {W}multi token?")
    choice = get_input("Selection")
    
    if choice == "1":
        t = get_input("Token")
        tokens = [t.strip()]
    else:
        try:
            with open("tokens.txt", "r") as f:
                tokens = [line.strip() for line in f if line.strip()]
            print(f"{G}[{R1}!{G}] {W}Loaded {len(tokens)} tokens.")
        except FileNotFoundError:
            print(f"{R1}Error: tokens.txt not found.")
            sys.exit()

    delay = float(get_input("Delay"))
    length = int(get_input("Length"))
    
    use_nums = get_input("Numbers? y/n").lower() == 'y'
    use_lets = get_input("Letters? y/n").lower() == 'y'
    use_syms = get_input("Symbols? y/n").lower() == 'y'

    char_pool = ""
    if use_lets: char_pool += string.ascii_lowercase
    if use_nums: char_pool += string.digits
    if use_syms: char_pool += "_."
    
    if not char_pool:
        char_pool = string.ascii_lowercase

    return delay, length, char_pool

def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": tokens[current_token_index]
    }

def check_username(username):
    global current_token_index
    if username in checked_usernames:
        return False
    
    checked_usernames.add(username)
    
    try:
        res = requests.post(URL, headers=get_headers(), json={"username": username})
        
        if res.status_code == 429:
            data = res.json()
            retry_after = data.get("retry_after", 5)
            if len(tokens) > 1:
                current_token_index = (current_token_index + 1) % len(tokens)
                return check_username(username)
            else:
                print(f"{G}[{R1}!{G}] {R3}Rate limit. Sleep {retry_after}s")
                time.sleep(retry_after)
                return check_username(username)

        if res.status_code == 200:
            data = res.json()
            if data.get("taken") is False:
                print(f"{G}[{R1}+{G}] {W}{username} {R1}AVAILABLE")
                with open(av_list, "a") as f:
                    f.write(f"{username}\n")
            else:
                print(f"{G}[{R1}-{G}] {R3}{username} taken")
        else:
            print(f"{G}[{R1}!{G}] {R4}Token Error or Invalid Response")
            
    except Exception:
        pass

def main():
    delay, length, pool = setup()
    
    print(f"\n{G}[{R1}!{G}] {W}Checking Token Validity...")
    try:
        r = requests.get(SYS_URL, headers=get_headers())
        user = r.json()['username']
        print(f"{G}[{R1}*{G}] {W}Logged in as: {R1}{user}\n")
    except:
        print(f"{R1}Authentication Failed.")
        return

    # To avoid infinite loops if the pool is too small for the length
    max_possibilities = len(pool) ** length
    
    while len(checked_usernames) < max_possibilities:
        target = ''.join(random.choices(pool, k=length))
        if target not in checked_usernames:
            check_username(target)
            time.sleep(delay)
    
    print(f"{G}[{R1}!{G}] {W}All possible combinations checked.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R1}Session Ended.")
        sys.exit()