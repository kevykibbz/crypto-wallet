import requests

APP_KEY = '7g3ybtmd1y4cb98'
APP_SECRET = 'dpntkn7hvfxx0ax'
REDIRECT_URI = 'https://your_redirect_uri'
AUTH_CODE = 'authorization_code_from_redirect_uri'

token_url = 'https://api.dropboxapi.com/oauth2/token'
data = {
    'code': AUTH_CODE,
    'grant_type': 'authorization_code',
    'client_id': APP_KEY,
    'client_secret': APP_SECRET,
    'redirect_uri': REDIRECT_URI
}

response = requests.post(token_url, data=data)
tokens = response.json()

access_token = tokens.get('access_token')
refresh_token = tokens.get('refresh_token')
print('Access Token:', access_token)
print('Refresh Token:', refresh_token)
