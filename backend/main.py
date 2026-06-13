from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response
from config import settings
from database import engine
from sqlalchemy import text
from urllib.parse import urlencode
import uuid
import httpx
import jwt


app=FastAPI()

linkedin_client_id=settings.CLIENT_ID
linkedin_client_secret=settings.CLIENT_SECRET

LINKEDIN_OAUTH_URL="https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_ACCESS_TOKEN_URL="https://www.linkedin.com/oauth/v2/accessToken"
REDIRECT_URI="http://localhost:8000/auth/callback"
LINKEDIN_BASIC_INFO_URL="https://api.linkedin.com/v2/me"


IS_PRODUCTION = not settings.FRONTEND_URL.startswith("http://localhost")

COOKIE_SETTINGS = {
    "key": "token",
    "httponly": True,
    "samesite": "none" if IS_PRODUCTION else "lax",
    "secure": IS_PRODUCTION,
}


def init_db():
    conn=engine.connect()
    with open("migrations/init.sql") as f:
        conn.execute(text(f.read()))
        conn.commit()

init_db() 

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


@app.get('/auth/callback')
async def auth_callback(code:str,state:str,error:str|None = None):
    if (error):
        return Response("failed",401)
    async with httpx.AsyncClient() as client:
        response=await client.post(
            LINKEDIN_ACCESS_TOKEN_URL,data={
            "grant_type":"authorization_code",
            "code":code,
            "client_id":linkedin_client_id,
            "client_secret":linkedin_client_secret,
            "redirect_uri":REDIRECT_URI,
            }  
        )
    result=response.json()
    access_token=result.get("access_token")
    refresh_token=result.get("refresh_token")
    expire_time=result.get("expires_in")
    async with httpx.AsyncClient() as client:
        user_info_response=await client.get(
            LINKEDIN_BASIC_INFO_URL,
            headers={"authorization":f"Bearer {access_token}"}
        )
    user_info=user_info_response.json()
    email=user_info.get("email")
    id=uuid.uuid4()
    connect=engine.connect()
    connect.execute(text("INSERT INTO USER (id,email,linkedin_access_token,linkedin_refresh_token,linkedin_token_expires_at) VALUES(:id,:email,:access_token,:refresh_token,:expire_time"),
    {"id":id,"email":email,":access_token":access_token,"refresh_token":refresh_token,"expire_time":expire_time}
    )
    connect.commit()
    jwt_token=jwt.encode({"sub":email},settings.JWT_SECRET,algorithm="HS256")
    response= RedirectResponse(url=f"{settings.FRONTEND_URL}/user")
    response.set_cookie(value=jwt_token, **COOKIE_SETTINGS)
    return response

