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
LINKEDIN_EMAIL_URL="https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"


IS_PRODUCTION = not settings.FRONTEND_URL.startswith("http://localhost")

COOKIE_SETTINGS = {
    "key": "token",
    "httponly": True,
    "samesite": "none" if IS_PRODUCTION else "lax",
    "secure": IS_PRODUCTION,
}


def init_db():
    with engine.connect() as conn:
        with open("migrations/init.sql") as f:
            statements = f.read().split(";")
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    conn.execute(text(stmt))
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
async def auth_callback(code:str,state:str|None=None,error:str|None = None):
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
    print (refresh_token,"this is refresh token")
    expire_time=result.get("refresh_token_expires_in")
    
    async with httpx.AsyncClient() as client:
        email_response=await client.get(
            LINKEDIN_EMAIL_URL,
            headers={"Authorization":f"Bearer {access_token}"}
        )
    email="rishirawat2021@gmail.com"

    
    id=str(uuid.uuid4())
    with engine.connect() as connect:
        connect.execute(text('INSERT INTO "USER" (id,email,linkedin_access_token,linkedin_refresh_token,linkedin_token_expires_at) VALUES(:id,:email,:access_token,:refresh_token,:expire_time)'),
        {"id":id,"email":email,"access_token":access_token,"refresh_token":refresh_token,"expire_time":expire_time}
        )
        connect.commit()
    
    jwt_token=jwt.encode({"sub":email,"userid":id},settings.JWT_SECRET,algorithm="HS256")
    res= RedirectResponse(url=f"{settings.FRONTEND_URL}/user")
    res.set_cookie(value=jwt_token, **COOKIE_SETTINGS)
    return res

