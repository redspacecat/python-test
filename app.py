import scratchattach as sa
import requests
import urllib.request
from PIL import Image
import json, os, random, math, time, io
from keep_alive import keep_alive
from collections.abc import MutableMapping
from dateutil import parser

def log(*args):
    print(f"[{round(time.time())}]", *args)

def convertToNumber (s):
    return int.from_bytes(s.encode(), 'little')

def convertFromNumber (n):
    return n.to_bytes(math.ceil(n.bit_length() / 8), 'little').decode()

def flatten(dictionary, parent_key='', separator='_'):
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)

imgs = {}

# if not os.path.isdir('/tmp/pfps'):
#     os.mkdir('/tmp/pfps')

session_id = os.environ.get("SESSION_ID")
session = sa.login_by_id(session_id, username=os.environ.get("USERNAME")) #replace with your session_id and username
cloud1 = session.connect_cloud(992640266) #replace with your project id
client1 = cloud1.requests()
cloud2 = session.connect_cloud(996217996)
client2 = cloud2.requests()
cloud3 = session.connect_cloud(1186288264)
client3 = cloud3.requests()
cloud4 = sa.get_tw_cloud(1186288264) # turbowarp version
client4 = cloud4.requests()

##
## Message count loader
##

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


##
## Profile Picture Viewer
##

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
    try:
        img = Image.open(f"/tmp/{img_id}").convert("RGBA") #open image based on id
    except:
        log("Failed to get image data from", img_id, "by", username)
        return "Error getting image data"
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

##
## Scratch Explorer
##

# Functions
def handle_ping(username): #called when client receives request
    print(f"Ping for Scratch Explorer from {username}")
    return "pong" #sends back 'pong' to the Scratch project

def handle_get_user_data(username): #called when client receives request
    print(f"getting data for {username}")
    try:
        r = requests.get(f"https://scratch-info.vercel.app/api/v1/users/{username}/info?mode=all", timeout=6)
    except requests.exceptions.Timeout:
        try:
            r = requests.get(f"https://scratch-info.vercel.app/api/v1/users/{username}/info?mode=all", timeout=6)
        except requests.exceptions.Timeout:
            return "Timeout error"
        
    if (r.text == "404"):
        return "Not Found"
    else:
        r = r.json()
    data = []
    for key, value in r.items():
        if (key == "joinDate"):
            value = value.split(",")[0]
        data.append(key)
        data.append(value)
    print(f"returning data for {username}")
    return data

def handle_get_project_data(id):
    try:
        id = round(int(id))
    except:
        return "Invalid project id"
    
    print("Getting data for project id", id)
    
    try:
        r = requests.get(f"https://scratch-info.vercel.app/api/v1/projects/{id}/info", timeout=6)
    except requests.exceptions.Timeout:
        try:
            r = requests.get(f"https://scratch-info.vercel.app/api/v1/projects/{id}/info", timeout=6)
        except requests.exceptions.Timeout:
            return "Timeout error"

    if (r.text == "404"):
        return "Not Found" 
    r = flatten(r.json())
    data = []
    for key, value in r.items():
        if ("history" in key):
            date = parser.parse(value)
            value = f"{date.month}/{date.day}/{date.year}"
        if ("stats" in key):
            value = "{:,}".format(value)
        if (key == "reviewStatus"):
            if value == "notreviewed":
                value = "Not Reviewed"
            elif value == "safe":
                value = "Safe (FE)"
            elif value == "notsafe":
                value = "Not Safe (NFE)"
        data.append(key)
        data.append(value)

    print("Returning data for project id", id)
    return data


def handle_get_project_thumb_hq(id):
    try:
        img_url = f"https://uploads.scratch.mit.edu/get_image/project/{id}_480x360.png"
        r = requests.get(img_url)
        img_id = random.randint(0, 10000000)
        imgs[img_id] = io.BytesIO(r.content)
        print("Getting hq project thumb for id", id)
        return img_id
    except:
        return "Error"

def handle_get_image_piece(img_id, y_offset, width, height, username): #call this function with different amounts of offset to get the image
    img_id = img_id.replace("/", "").replace("\\", "")
    img = Image.open(imgs[int(img_id)]).convert("RGBA") #open image based on id
    img = img.resize((int(width), int(height)))
    width, height = img.size
    pixels = img.load()

    amount = 10

    colors = [] #construct colors list
    for y in range(int(y_offset), int(y_offset) + int(amount)): #get a specific chunk of the image
        for x in range(width):
            r, g, b, a = pixels[x, y]
            color = a * 16777216 + r * 65536 + g * 256 + b
            colors.append(color)
    print(username, 'requested image piece for image "' + img_id + '" with y offset', y_offset)
    return colors #return data

def handle_stats(username):
    print("getting project stats for", username)
    try:
        r = requests.get(f"https://scratch-info.vercel.app/api/v1/users/{username}/projectStats", timeout=6).json()
    except requests.exceptions.Timeout:
        try:
            r = requests.get(f"https://scratch-info.vercel.app/api/v1/users/{username}/projectStats", timeout=6).json()
        except requests.exceptions.Timeout:
            r = {}
    
    try:
        r["mp"] = r["projects"][0]
    except IndexError:
        return "Not Found"
    if "projects" in r:
        del r["projects"]
    print("returning stats for", username)

    data = []
    for key, value in r.items():
        if (key == "averageStats"):
            data.append("averageViews")
            data.append("{:,}".format(round(value["averageViews"])))
            data.append("averageLoves")
            data.append("{:,}".format(round(value["averageLoves"])))
            data.append("averageFaves")
            data.append("{:,}".format(round(value["averageFaves"])))
        else:
            if (key == "mp"):
                data.append("p_loves")
                data.append("{:,}".format(round(value["loves"])))
                data.append("p_faves")
                data.append("{:,}".format(round(value["faves"])))
                data.append("p_views")
                data.append("{:,}".format(round(value["views"])))
                data.append("p_id")
                data.append(value["id"])
                data.append("p_loveToViewRatio")
                data.append(round(value["loveToViewRatio"], 2))
                data.append("p_title")
                data.append(value["title"])
            else: 
                data.append(key)
                data.append("{:,}".format(value))
    return data


def handle_pfp(username, resolution):
    try:
        print(f"Profile picture requested for {username}")

        user = sa.get_user(username).id
        url = "https://uploads.scratch.mit.edu/get_image/user/" + str(user) + "_100x100.png"
        r = requests.get(url)

        img = Image.open(io.BytesIO(r.content)).convert("RGBA")
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
    except:
        return "User Not Found"
    

def handle_project_thumbnail(id, higher_quality, isTw=False):
    try:
        print(f"Project thumbnail requested for {id}")

        if higher_quality == "1":
            if (isTw):
                url = "https://uploads.scratch.mit.edu/get_image/project/" + str(id) + "_80x60.png"
            else:
                url = "https://uploads.scratch.mit.edu/get_image/project/" + str(id) + "_40x30.png"
        else:
            url = "https://uploads.scratch.mit.edu/get_image/project/" + str(id) + "_20x15.png"
        r = requests.get(url)

        img = Image.open(io.BytesIO(r.content)).convert("RGBA")
        # img = img.resize((int(resolution), int(resolution)))
        width, height = img.size
        pixels = img.load()

        colors = []
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                color = a * 16777216 + r * 65536 + g * 256 + b
                colors.append(color)
        return colors
    except:
        return "Error getting project thumbnail"

@client3.request
def ping(*args):
    return handle_ping(*args)
@client3.request
def get_user_data(*args):
    return handle_get_user_data(*args)
@client3.request
def get_project_data(*args):
    return handle_get_project_data(*args)
@client3.request
def get_project_thumb_hq(*args):
    return handle_get_project_thumb_hq(*args)
@client3.request
def get_image_piece(*args):
    return handle_get_image_piece(*args)
@client3.request
def stats(*args):
    return handle_stats(*args)
@client3.request
def pfp(*args):
    return handle_pfp(*args)
@client3.request
def project_thumbnail(*args):
    return handle_project_thumbnail(*args)

@client3.event
def on_ready():
    print("Request handler for Scratch Explorer on Scratch is running")

@client4.request
def ping(*args):
    return handle_ping(*args)
@client4.request
def get_user_data(*args):
    return handle_get_user_data(*args)
@client4.request
def get_project_data(*args):
    return handle_get_project_data(*args)
@client4.request
def get_project_thumb_hq(*args):
    return handle_get_project_thumb_hq(*args)
@client4.request
def get_image_piece(*args):
    return handle_get_image_piece(*args)
@client4.request
def stats(*args):
    return handle_stats(*args)
@client4.request
def pfp(*args):
    return handle_pfp(*args)
@client4.request
def project_thumbnail(*args):
    return handle_project_thumbnail(*args, True)

@client4.event
def on_ready():
    print("Request handler for Scratch Explorer on Turbowarp is running")

keep_alive()
client1.start()
client2.start()
client3.start()
client4.start()
log("Started stuff")