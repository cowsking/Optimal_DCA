from coinbase import jwt_generator
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

import jwt
from cryptography.hazmat.primitives import serialization
import time
import secrets

request_method = "GET"
request_host   = "api.coinbase.com"
request_path   = "/api/v3/brokerage/accounts"
def build_jwt(uri):
    private_key_bytes = API_SECRET.encode('utf-8')
    private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
    jwt_payload = {
        'sub': API_KEY,
        'iss': "cdp",
        'nbf': int(time.time()),
        'exp': int(time.time()) + 120,
        'uri': uri,
    }
    jwt_token = jwt.encode(
        jwt_payload,
        private_key,
        algorithm='ES256',
        headers={'kid': API_KEY, 'nonce': secrets.token_hex()},
    )
    return jwt_token
def main():
    uri = f"{request_method} {request_host}{request_path}"
    jwt_token = build_jwt(uri)
    # print(jwt_token)
    # Make the API request
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    response = requests.get(f"https://{request_host}{request_path}", headers=headers)
    print(response.json())  # Return the JSON response
if __name__ == "__main__":
    main()