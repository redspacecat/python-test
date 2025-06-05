import scratchattach as sa
import requests
import urllib.request
from PIL import Image
import json, os
from keep_alive import keep_alive

session_id = os.environ.get("SESSION_ID")
session = sa.login_by_id(session_id, username=os.environ.get("USERNAME")) #replace with your session_id and username
cloud1 = session.connect_cloud(992640266) #replace with your project id
client1 = cloud1.requests()
cloud2 = session.connect_cloud(996217996)
client2 = cloud2.requests()

@client1.request
def ping(): #called when client receives request
    print("Ping request received")
    return "pong"

@client1.request
def message_count(username): #called when client receives request
    print("Getting message count for", username)
    try:
        r = requests.get(f"https://api.scratch.mit.edu/users/{username}/messages/count")
        count = json.loads(r.text)["count"]
    except:
        return "Error"
    return count

@client1.event
def on_ready():
    print("Request handler for message count is running")


@client2.request
def ping(): #called when client receives request
    print("Ping request received")
    return "pong" #sends back 'pong' to the Scratch project

@client2.request
def pfp(username, resolution):
        print(f"Profile picture requested for {username}")

        try:
            user = sa.get_user(username).id
        except:
            return "User Not Found"
        url = "https://uploads.scratch.mit.edu/get_image/user/" + str(user) + "_100x100.png"
        urllib.request.urlretrieve(url, "/tmp/avatar.png")

        img = Image.open("/tmp/avatar.png").convert("RGBA")
        img = img.resize((int(resolution), int(resolution)))
        width, height = img.size
        pixels = img.load()

        colors = []
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                color = a * 16777216 + r * 65536 + g * 256 + b
                colors.append(color)
        return colors

@client2.event
def on_ready():
    print("Request handler for pfp loader is running")

keep_alive()
client1.start()
client2.start()
print("Started stuff")