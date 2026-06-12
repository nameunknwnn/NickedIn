from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from config import settings
from urllib.parse import urlencode

app=FastAPI()


linkedin_client_id=settings.CLIENT_ID
print(linkedin_client_id,"hiiiiii")
linkedin_client_secret=settings.CLIENT_SECRET

LINKEDIN_OAUTH_URL="https://www.linkedin.com/oauth/v2/authorization"
REDIRECT_URI="https://localhost:8000/auth/callback"

@app.get('/linked/auth')
async def linked_auth():
    params={
        "response_type":"code",
        "client_id":linkedin_client_id,
        "redirect_uri":REDIRECT_URI,
        "scope":"openid profile email"
        }
    
    auth_url=f"{LINKEDIN_OAUTH_URL}?{urlencode(params)}"
    print(auth_url)
    return RedirectResponse(auth_url)