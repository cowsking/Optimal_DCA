from coinbase import jwt_generator
import requests
import jwt
from cryptography.hazmat.primitives import serialization
import time
import secrets
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

request_method = "POST" 
request_host = "api.coinbase.com"
request_path = "/v2/accounts/8a7eea6a-f402-5df0-8baf-b510237b5c60/deposits"

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

def deposit_funds():
    uri = f"{request_method} {request_host}{request_path}"
    jwt_token = build_jwt(uri)
    
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    data = {
        "amount": "10",
        "currency": "USD", 
        "payment_method": "faeea233-4182-58f6-b55d-35da447bd79f"
    }

    response = requests.post(f"https://{request_host}{request_path}", headers=headers, json=data)
    return response.json()

if __name__ == "__main__":
    result = deposit_funds()
    print(result)