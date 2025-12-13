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

superscript_numbers = [
    "⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"
]
normal_numbers = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
]



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

# Modified version of the Above ^
def secondsToTimeH(seconds):
    seconds = int(seconds)  # convert float → int
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{minutes:2d}:{seconds:02d}"

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
        "is_playing": current["is_playing"],
        "progress": current["progress_ms"],
        "duration": item["duration_ms"]
    }



def progressbar(progress, duration):
    barstr = ""
    progstr = ""
    durastr = ""
    timeindex = round(((progress/1000)/(duration/1000))*10)
    for i in range(0, 11):
        if i <= timeindex: 
            barstr = barstr + "▓"
        else: barstr = barstr + "░"
    
    ts = secondsToTimeH(progress/1000)
    first = False
    first2 = False

    for c in secondsToTimeH(duration/1000):
        try:
            sixseven2 = normal_numbers.index(c)
            durastr = durastr + superscript_numbers[sixseven2]
        except ValueError:
            if first2:
                durastr = durastr + "'"
            else: first2 = True

    for pmo in ts:
        try:
            sixseven = normal_numbers.index(pmo)
            progstr = progstr + superscript_numbers[sixseven]
        except ValueError:
            if first:
                progstr = progstr + "'"
            else: first = True
    return(f"{progstr} {barstr} {durastr}")




with open("bin/status.txt", "r", encoding="utf-8") as file:
    content = file.read()
    statmsg = str(content).splitlines()
    
with open("bin/emojis.txt", "r", encoding="utf-8") as file:
    emojis = file.read().split(",")

afkbin = False
indexstat = 0
restindex = 0
statchangeindex = 0
while True:
    spotstr = "⏸️"
    spotifyret = get_current_spotify_song()
    if spotifyret:
        titless = str(spotifyret["title"])
        if len(str(spotifyret["title"])) > 18:
            titless = insert_string_at_index(str(spotifyret["title"]), "...[]]\-=", 17)
        spotemoji = "⏸️"
        if spotifyret["is_playing"]:
            spotemoji = "🎵"
        spotstr = f"{spotemoji} {titless.split('[]]\-=')[0]} ᵇʸ {spotifyret['artist']}\n{progressbar(spotifyret["progress"], spotifyret["duration"])}"
        
    if statchangeindex == 0:
        try: mainstat = statmsg[indexstat]
        except IndexError: indexstat = 0
    
        txtindex = 0
        txtlimreached = False
        newerstatmsg = ""
        if len(mainstat) > 23:
            basestat = mainstat.split()
            for txt in basestat:
                newerstatmsg = newerstatmsg + txt + " "
                if not txtlimreached:
                    for c in txt:
                        txtindex += 1
                        if txtindex == 23:
                            txtlimreached = True
                            newerstatmsg = newerstatmsg + "\n"

                        continue
        if len(mainstat) <= 23: 
            oldstatstr = f"{random.choice(emojis)} {statmsg[indexstat]}"
            statstr = f"{random.choice(emojis)} {mainstat}"
        if txtlimreached:
            mainstat = newerstatmsg
            oldstatstr = f"{random.choice(emojis)} {statmsg[indexstat]}"
            statstr = f"{random.choice(emojis)} {mainstat}"

    with open("bin/afk", "r") as file:
        if file.read() == "False": afk = False
        else: afk = True
    
    if afk:
        if not afkbin:
            start_time = time.time()
            afkbin = True
        statstr = f"☕ ᶜᵘʳʳᵉⁿᵗˡʸ ᵃᶠᵏ ᶠᵒʳ {secondsToTime(time.time() - start_time)}"
    else: afkbin = False


    with open("bin/chatboxcontent", "r", encoding="utf-8") as file:
        chatbox = file.read()

    localtime = time.localtime()
    hour = localtime.tm_hour
    if hour / 12 >= 1:
        adj = "PM"
        hour -= 12
    else: 
        adj = "AM"
        hour = 12

    timestr = f"{f"{hour}:{localtime.tm_min:02d} {adj}".center(3)}"


    endstr = f"{oldstatstr}\n{timestr}\n{spotstr}\n{chatbox}"

    client.send_message("/chatbox/input", [endstr, True, False])
    if restindex >= 100: 
        client._sock.close()
        client = SimpleUDPClient(ip, port)
        restindex = 0

    restindex += 1
    with open("bin/chatboxcurrent", "w", encoding="utf-8") as file:
        file.write(f"{statstr}\n{timestr}\n{spotstr}\n{chatbox}")
    statchangeindex += 1
    if statchangeindex >= 3: 
        statchangeindex = 0
        indexstat += 1

    time.sleep(2)
