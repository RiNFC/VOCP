from pythonosc.udp_client import SimpleUDPClient
import time
import dotenv
import os
import random
import subprocess

dotenv.load_dotenv()

ip = "127.0.0.1"
port = 9000

client = SimpleUDPClient(ip, port)

import spotipy
from spotipy.oauth2 import SpotifyOAuth
with open("bin/timeindex", 'r', encoding="utf-8") as file:
    core_start = float(file.read())



CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"

def insert_string_at_index(original_string, string_to_insert, index):
    return original_string[:index] + string_to_insert + original_string[index:]

# https://www.reddit.com/r/learnpython/comments/2gpckp/comment/ckl9z9f
# Was too lazy to make my own.
def secondsToTime(seconds):
    seconds = int(seconds)  # convert float → int
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"



def get_current_spotify_song():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-read-currently-playing"
    ))

    current = sp.current_user_playing_track()
    if current is None or current.get("item") is None:
        return {}

    item = current["item"]
    return {
        "title": item["name"],
        "artist": item["artists"][0]["name"],
        "album": item["album"]["name"],
        "is_playing": current["is_playing"]
    }


# I have No idea what I am doing here but It Kinda Works
def get_gpu_status_no_popup():
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            creationflags=0x08000000
        )
        gpus = []
        for line in result.stdout.strip().split("\n"):
            index, name, mem_total, mem_used, load = line.split(", ")
            gpus.append(
                type("GPU", (object,), {
                    "id": int(index),
                    "name": name,
                    "memoryTotal": float(mem_total)/1000,
                    "memoryUsed": float(mem_used)/1000,
                    "load": float(load)/100
                })()
            )
        return gpus

with open("bin/status.txt", "r", encoding="utf-8") as file:
    content = file.read()
    statmsg = str(content).splitlines()
    
with open("bin/emojis.txt", "r", encoding="utf-8") as file:
    emojis = file.read().split(",")

afkbin = False
indexstat = 0
restindex = 0
while True:
    gpus = get_gpu_status_no_popup()
    gpu = gpus[0]
    spotstr = "⏸️"
    spotifyret = get_current_spotify_song()
    if spotifyret:
        titless = str(spotifyret["title"])
        if len(str(spotifyret["title"])) > 18:
            titless = insert_string_at_index(str(spotifyret["title"]), "...[]]\-=", 17)
        spotemoji = "⏸️"
        if spotifyret["is_playing"]:
            spotemoji = "🎵"
        spotstr = f"{spotemoji} {titless.split('[]]\-=')[0]} ᵇʸ {spotifyret['artist']}"

    try: 
        statstr = f"{random.choice(emojis)} {statmsg[indexstat]}"
    except IndexError: 
        indexstat = 0
        with open("bin/timeindex", 'r', encoding="utf-8") as file:
            core_start = float(file.read())
        statstr = f"{random.choice(emojis)} {statmsg[indexstat]}"

    with open("bin/afk", "r") as file:
        if file.read() == "False": afk = False
        else: afk = True
    
    if afk:
        if not afkbin:
            start_time = time.time()
            afkbin = True
        statstr = f"💤 ᶜᵘʳʳᵉⁿᵗˡʸ ᵃᶠᵏ ᶠᵒʳ {secondsToTime(time.time() - start_time)}"
    else: afkbin = False

    gpustat = f"ᵍᵖᵘ {int(gpu.load*100)}% ¦ ᵛʳᵃᵐ {round(gpu.memoryUsed, 1 )}/{round(gpu.memoryTotal, 1)}Gb"

    with open("bin/chatboxcontent", "r", encoding="utf-8") as file:
        chatbox = file.read()


    timestr = f"⏱️ ᴾˡᵃʸ ᵀᶦᵐᵉ {secondsToTime(time.time() - core_start)}"


    endstr = f"{statstr}\n{gpustat}\n{timestr}\n{spotstr}\n{chatbox}"

    client.send_message("/chatbox/input", [endstr, True, False])
    if restindex >= 100: 
        client._sock.close()
        client = SimpleUDPClient(ip, port)
        restindex = 0

    restindex += 1
    with open("bin/chatboxcurrent", "w", encoding="utf-8") as file:
        file.write(endstr)
    indexstat += 1

    time.sleep(2)
