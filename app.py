import scratchattach as sa
import requests
import urllib.request
from PIL import Image
import json, os, random, base64
from keep_alive import keep_alive


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


# @client2.request
# def ping(): #called when client receives request
#     print("Ping request received")
#     return "pong" #sends back 'pong' to the Scratch project

# @client2.request
# def pfp(username, resolution):
#         print(f"Profile picture requested for {username}")

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
#     print("Request handler for pfp loader is running")

@client2.request
def ping(): #called when client receives request
    print(f"Ping")
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
    print(f"Image url: {img_url}")
    image_name = f"pfp{random.randint(0, 10000000)}.png" #give image unique id
    # image_name = f"pfp{base64.b64encode(username.encode()).decode('utf-8')}.png"
    urllib.request.urlretrieve(img_url, f"/tmp/{image_name}")
    # print(f"Image stored in: {os.path.join("/tmp", 'pfps', image_name)}")
    print(f"Image stored in /tmp/{image_name}")
    # try:
    #     with open(f"/tmp/pfps/{image_name}", "wb") as f:  #store image
    #         f.write(r.content)
    # except Exception as e:
    #     print(e)
    #     print(e.with_traceback())

    # img_url = requests.get(f"https://tinyurl.com/api-create.php?url={urllib.parse.quote_plus(img_url)}").text
    print("img id", image_name)
    return image_name #return image data
            
    # except Exception:
    #     print("There was a error")
    #     return "There was a error."

@client2.request
def get_image_piece(img_id, y_offset, img_size, username): #call this function with different amounts of offset to get the image
    img_id = img_id.replace("/", "").replace("\\", "")
    # try:
    img = Image.open(f"/tmp/{img_id}").convert("RGBA") #open image based on id
    # except:
        # print("File", img_id, "doesn't exist, replacing file...")
        # get_pfp(base64.b64decode(str(img_id).replace("pfp", "").replace(".png", "")).decode("utf-8"))
        # img = Image.open(f"/tmp/{img_id}").convert("RGBA") #open image based on id
        # print("Done replacing")
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
    print(username, 'requested image piece for image "' + img_id + '" with y offset', y_offset)
    return colors #return data

@client2.request
def done(img_id):
    try:
        os.remove(f'/tmp/{str(img_id)}')
        print("Removing file", img_id)
        return "Done"
    except:
        return "Error deleting file"

@client2.event
def on_ready():
    print("Request handler is running")

keep_alive()
client1.start()
client2.start()
print("Started stuff")