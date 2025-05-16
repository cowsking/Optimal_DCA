from coinbase import jwt_generator

api_key = ""
api_secret = ""

request_method = "GET"
request_path = "/api/v3/brokerage/accounts"

def main():
    jwt_uri = jwt_generator.format_jwt_uri(request_method, request_path)
    jwt_token = jwt_generator.build_rest_jwt(jwt_uri, api_key, api_secret)
    print(jwt_token)

if __name__ == "__main__":
    main()