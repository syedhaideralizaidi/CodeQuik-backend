import requests

def validate_google_token(access_token):
    # Validate the token by calling the Google token info endpoint
    validate_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={access_token}"
    response = requests.get(validate_url)
    return response.json() if response.status_code == 200 else None