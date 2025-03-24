import requests

def validate_google_token(access_token):
    # Validate the token by calling the Google token info endpoint
    validate_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={access_token}"
    response = requests.get(validate_url)
    return response.json() if response.status_code == 200 else None


def get_token_limit(product_name):
    if product_name == 'MonthlyPro':
        return 5000000
    elif product_name == 'MonthlyPro50':
        return 26000000
    elif product_name == 'MonthlyPro100':
        return 55000000
    elif product_name == 'MonthlyPro200':
        return 120000000
    elif product_name == 'Yearly Pro -10M':
        return 100000000
    elif product_name == 'Yearly Pro 50 - 100M':
        return 100000000
    elif product_name == 'Yearly Pro 100 - 200M':
        return 200000000
    elif product_name == 'Yearly Pro 200 - 400M':
        return 400000000

    else:
        return None  # or raise an exception if needed
