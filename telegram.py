from pyngrok import ngrok
import os
from dotenv import load_dotenv

load_dotenv()

# Get auth token from environment variable
auth_token = os.getenv('NGROK_AUTH_TOKEN')

if not auth_token:
    raise ValueError("NGROK_AUTH_TOKEN not set in environment variables")

ngrok.set_auth_token(auth_token)
tunnel = ngrok.connect(5000, bind_tls=True)
print(f"Public URL: {tunnel.public_url}")