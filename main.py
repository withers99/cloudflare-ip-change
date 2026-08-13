import os
from dotenv import load_dotenv
from cloudflare import Cloudflare
import requests
import subprocess
# Define vairables
found = 0
# Load local environment variables
load_dotenv()

# Extract API keys and account detials
account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
api_token= os.getenv("CLOUDFLARE_API_TOKEN")
list_id = os.getenv("CLOUDFLARE_LIST_ID")
if not api_token or not account_id:
    raise ValueError("Missing Cloudflare credentials in environment variables.")

# Setup cloudflare client
client = Cloudflare(api_token=api_token)

# Fetch list using Cloudflare API
items_response = client.rules.lists.items.list(
    list_id=list_id,
    account_id=account_id,
    per_page=500
)

# Put the IP's into a list
entries = [getattr(e, "ip", None) or getattr(e, "value", None) for e in items_response if getattr(e, "ip", None) or getattr(e, "value", None)]
# Get the current public IP address
ip = requests.get('https://api.ipify.org').text
for i in entries:
    if i == ip:
        found = 1
        break
if found == 0: 
    try:
        items_response = client.rules.lists.items.create( 
            list_id=list_id,
            account_id=account_id,
            body=[{ "ip": ip }]
        )
        print("IP successfully added to Cloudflare list.")
        
    except Cloudflare.APIStatusError as e:
        subprocess.run([
            "/usr/local/bin/notify.sh", 
            "Cloudflare error", 
            "The public IP address has changed, but the script failed"
        ])
    else:
        subprocess.run([
            "/usr/local/bin/notify.sh", 
            "Cloudflare alert", 
            "The public IP address has changed, you need to remove the old IP!"
        ])


    