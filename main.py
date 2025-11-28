from pythonosc.udp_client import SimpleUDPClient
import time
import GPUtil
import dotenv
import os
import random

dotenv.load_dotenv()

gpus = GPUtil.getGPUs()
gpu = gpus[0]
    

ip = "127.0.0.1"
port = 9000

client = SimpleUDPClient(ip, port)

import spotipy
from spotipy.oauth2 import SpotifyOAuth


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"

def insert_string_at_index(original_string, string_to_insert, index):
    return original_string[:index] + string_to_insert + original_string[index:]

def clearchatbox():
    client.send_message("/chatbox/input", ["", True, False])

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
        "artist": ", ".join(artist["name"] for artist in item["artists"]),
        "album": item["album"]["name"],
        "is_playing": current["is_playing"]
    }

with open("bin/status.txt", "r", encoding="utf-8") as file:
    content = file.read()
    statmsg = str(content).splitlines()
with open("bin/emojis.txt", "r", encoding="utf-8") as file:
    emojis = file.read().split(",")

indexstat = 0
while True:
    spotstr = ""
    spotifyret = get_current_spotify_song()
    if spotifyret:
        titless = str(spotifyret["title"])
        if len(str(spotifyret["title"])) > 18:
            titless = insert_string_at_index(str(spotifyret["title"]), "...[]]\-=", 17)
        spotemoji = "⏸️"
        if spotifyret["is_playing"]:
            spotemoji = "🎵"
        spotstr = f"{spotemoji} {titless.split("[]]\-=")[0]} ᵇʸ {spotifyret["artist"]}"

    

    
    try: statstr = f"{random.choice(emojis)} {statmsg[indexstat]}"
    except IndexError: 
        indexstat = 0
        statstr = f"{random.choice(emojis)} {statmsg[indexstat]}"

    gpustat = f"ᵍᵖᵘ {int(gpu.load*100)}% ¦ᵛʳᵃᵐ {round(gpu.memoryUsed / 1000, 1)}/{round(gpu.memoryTotal / 1000, 1)}Gb"

    with open("bin/chatboxcontent", "r", encoding="utf-8") as file:
        chatbox = file.read()

    endstr = f"{statstr}\n{spotstr}\n{gpustat}\n{chatbox}"
    


    client.send_message("/chatbox/input", [endstr, True, False])
    with open("bin/chatboxcurrent", "w", encoding="utf-8") as file:
        file.write(endstr)
    indexstat += 1

    time.sleep(2)