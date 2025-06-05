import scratchattach as sa
import requests
import json, os

session_id = os.environ.get("SESSION_ID")
session = sa.login_by_id(session_id, username=os.environ.get("USERNAME")) #replace with your session_id and username
cloud = session.connect_cloud(1184958260) #replace with your project id
client = cloud.requests()

@client.request
def ping(): #called when client receives request
    print("Ping request received")
    return "pong"

@client.request
def message_count(username): #called when client receives request
    print("Getting message count for", username)
    # try:
    r = requests.get(f"https://api.scratch.mit.edu/users/{username}/messages/count")
    count = json.loads(r.text)["count"]
    # except:
    # return "There was an error while fetching message count"
    return count

@client.event
def on_ready():
    print("Request handler is running")

client.start(thread=True) # thread=True is an optional argument. It makes the cloud requests handler run in a thread