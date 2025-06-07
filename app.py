import scratchattach as sa
import requests
import urllib.request
from PIL import Image
import json, os, random, math, time
from keep_alive import keep_alive

def log(stuff):
    stuff.insert(0, f"[{round(time.time())}]")
    print(stuff)

def convertToNumber (s):
    return int.from_bytes(s.encode(), 'little')

def convertFromNumber (n):
    return n.to_bytes(math.ceil(n.bit_length() / 8), 'little').decode()

# if not os.path.isdir('/tmp/pfps'):
#     os.mkdir('/tmp/pfps')

session_id = os.environ.get("SESSION_ID")
session = sa.login_by_id(session_id, username=os.environ.get("USERNAME")) #replace with your session_id and username
cloud1 = session.connect_cloud(992640266) #replace with your project id
client1 = cloud1.requests()
cloud2 = session.connect_cloud(996217996)
client2 = cloud2.requests()

@client1.request
def ping(): #called when client receives request
    log("Ping request received for message count")
    return "pong"

@client1.request
def message_count(username): #called when client receives request
    log("Getting message count for", username)
    try:
        r = requests.get(f"https://api.scratch.mit.edu/users/{username}/messages/count")
        count = json.loads(r.text)["count"]
    except:
        return "Error"
    return count

@client1.event
def on_ready():
    log("Request handler for message count is running")


# @client2.request
# def ping(): #called when client receives request
#     log("Ping request received")
#     return "pong" #sends back 'pong' to the Scratch project

# @client2.request
# def pfp(username, resolution):
#         log(f"Profile picture requested for {username}")

#         try:
#             user = sa.get_user(username).id
#         except:
#             return "User Not Found"
#         url = "https://uploads.scratch.mit.edu/get_image/user/" + str(user) + "_100x100.png"
#         urllib.request.urlretrieve(url, "/tmp/avatar.png")

#         img = Image.open("/tmp/avatar.png").convert("RGBA")
#         img = img.resize((int(resolution), int(resolution)))
#         width, height = img.size
#         pixels = img.load()

#         colors = []
#         for y in range(height):
#             for x in range(width):
#                 r, g, b, a = pixels[x, y]
#                 color = a * 16777216 + r * 65536 + g * 256 + b
#                 colors.append(color)
#         return colors

# @client2.event
# def on_ready():
#     log("Request handler for pfp loader is running")

@client2.request
def ping(username): #called when client receives request
    log(f"Ping request received from {username}")
    return "pong" #sends back 'pong' to the Scratch project

@client2.request
def get_pfp(username):
    # try:
    try:
        user_id = sa.get_user(username).id
    except:
        return "User Not Found"
    img_url = f"https://uploads.scratch.mit.edu/get_image/user/{user_id}_100x100.png"
    # r = requests.get(img_url)
    log(f"Image url: {img_url}")
    # image_name = f"pfp{random.randint(0, 10000000)}.png" #give image unique id
    image_name = f"pfp{convertToNumber(username)}.png"
    urllib.request.urlretrieve(img_url, f"/tmp/{image_name}")
    # log(f"Image stored in: {os.path.join("/tmp", 'pfps', image_name)}")
    log(f"Image stored in /tmp/{image_name}")
    # try:
    #     with open(f"/tmp/pfps/{image_name}", "wb") as f:  #store image
    #         f.write(r.content)
    # except Exception as e:
    #     log(e)
    #     log(e.with_traceback())

    # img_url = requests.get(f"https://tinyurl.com/api-create.php?url={urllib.parse.quote_plus(img_url)}").text
    log("img id", image_name)
    return image_name #return image data
            
    # except Exception:
    #     log("There was a error")
    #     return "There was a error."

@client2.request
def get_image_piece(img_id, y_offset, img_size, username): #call this function with different amounts of offset to get the image
    img_id = img_id.replace("/", "").replace("\\", "")
    img = Image.open(f"/tmp/{img_id}").convert("RGBA") #open image based on id
    img = img.resize((int(img_size), int(img_size)))
    width, height = img.size
    pixels = img.load()

    amount = 10

    colors = [] #construct colors list
    for y in range(int(y_offset), int(y_offset) + int(amount)): #get a specific chunk of the image
        for x in range(width):
            r, g, b, a = pixels[x, y]
            color = a * 16777216 + r * 65536 + g * 256 + b
            colors.append(color)
    log(username, 'requested image piece for image "' + img_id + '" with y offset', y_offset)
    return colors #return data

@client2.request
def done(img_id):
    try:
        os.remove(f'/tmp/{str(img_id)}')
        log("Removing file", img_id)
        return "Done"
    except:
        return "Error deleting file"

@client2.event
def on_ready():
    log("Request handler is running")

keep_alive()
client1.start()
client2.start()
log("Started stuff")