from dotenv import load_dotenv
import requests
import os

load_dotenv()

JWT_TOKEN = os.getenv("JWT")
print(JWT_TOKEN)
# For instructions generating JWT, check the "API Key Authentication" section
JWT_TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6Im9yZ2FuaXphdGlvbnMvOWZiOWY5YWQtYjQ5Ni00OTRlLTlmZGQtNDBmYzk3OGFhNzJjL2FwaUtleXMvZjQwMDA2MDQtMGFkMS00ZDE4LThjOTItY2NjYTk1M2FlN2ViIiwibm9uY2UiOiJkMDZkYmE0NWFkNjIxMzY5NDMwMmFkN2QwNzY1M2Q2NTMwZWI0Yjk0MWE2OWI3ZjhiYTkyZjkwOWVlOGI2NzE0IiwidHlwIjoiSldUIn0.eyJzdWIiOiJvcmdhbml6YXRpb25zLzlmYjlmOWFkLWI0OTYtNDk0ZS05ZmRkLTQwZmM5NzhhYTcyYy9hcGlLZXlzL2Y0MDAwNjA0LTBhZDEtNGQxOC04YzkyLWNjY2E5NTNhZTdlYiIsImlzcyI6ImNkcCIsIm5iZiI6MTc0NzM2MjM2MCwiZXhwIjoxNzQ3MzYyNDgwLCJ1cmkiOiJHRVQgYXBpLmNvaW5iYXNlLmNvbS92Mi9hY2NvdW50cyJ9.8iubojljjDRtsMtbOZ_M9wFgIK8z2AVtjmTQa7TFGpCy74FgburR8Fw8LGq7geVUXXwBnemZkC8DO2zekxWtWQ"
# Coinbase API base URL
ENDPOINT_URL = "https://api.coinbase.com/v2/accounts/:account_id/deposits"

def deposit_funds():
    # Generate headers with JWT for authentication
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
    }

    data = {
      "amount": "10",
      "currency": "USD",
      "payment_method": "faeea233-4182-58f6-b55d-35da447bd79f"
    }

    # Make the API request
    response = requests.post(ENDPOINT_URL, data=data, headers=headers)

    print(response)  # Return the JSON response

deposit_funds = deposit_funds()
print(deposit_funds)