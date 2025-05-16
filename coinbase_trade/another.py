from coinbase import jwt_generator

api_key = "organizations/9fb9f9ad-b496-494e-9fdd-40fc978aa72c/apiKeys/c64bceee-5f14-4ac6-ad5f-b6221ceac9d6"
api_secret = "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEII7Mrt8clsAU1va5P0NhQs3uhzifAcqqOYpMr7+FP+sGoAoGCCqGSM49\nAwEHoUQDQgAEwbZfFDK4E8D+NWUwMnduZfq2O0V4CeiYdP7RgA//ZiNpGIjPo40s\nPLlGKArM6uh0tFTThpKW+/fX0KH2G65RoA==\n-----END EC PRIVATE KEY-----\n"

request_method = "GET"
request_path = "/api/v3/brokerage/accounts"

def main():
    jwt_uri = jwt_generator.format_jwt_uri(request_method, request_path)
    jwt_token = jwt_generator.build_rest_jwt(jwt_uri, api_key, api_secret)
    print(jwt_token)

if __name__ == "__main__":
    main()