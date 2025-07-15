# exchange_token.py
import requests
import os
from dotenv import load_dotenv
load_dotenv()



# Fill in these values:
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:8080"
auth_code = "bztika6ck5a2txeob429qhmzkot7ed"

response = requests.post("https://id.twitch.tv/oauth2/token", params={
    "client_id": client_id,
    "client_secret": client_secret,
    "code": auth_code,
    "grant_type": "authorization_code",
    "redirect_uri": redirect_uri
})

print(response.json())
