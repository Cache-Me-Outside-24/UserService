from typing import Union
from fastapi import FastAPI, Depends, HTTPException
from services.sql_comands import SQLMachine
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
import requests
import os
import json

load_dotenv()

config = Config(environ={
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET")
})

app = FastAPI()

oauth = OAuth(config)

app.add_middleware(SessionMiddleware, secret_key="123456")

google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    # This is only needed if using openId to fetch user info
    client_kwargs={"scope": "email profile"},
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs"
)

def get_user_info(access_token):
    auth = "Bearer " + access_token
    headers = {"Authorization": auth}
    rsp = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)

    try:
        result = rsp.json()
    except Exception as e:
        print("get_user_info: Exception = ", e)
        result = None

    return result


@app.get('/sign-up')
async def sign_up(request: Request):
    # Redirect the user to Google's OAuth2 authorization URL
    redirect_uri = 'http://localhost:8000/auth/callback'  # TODO: Change callback url to adapt to prod server
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth/callback') # TODO: should change to be separate from signup
async def auth(request: Request):
    # Get the token and user info after user authorization
    try:
        token = await oauth.google.authorize_access_token(request)
        access_token = token.get("access_token")

        # user = await oauth.google.parse_id_token(token)
        user = token.get('userinfo')
        # user2 = await oauth.google.parse_id_token(request, token)

        # Store user info in the session (you can store more details if needed)
        # request.session['user'] = dict(user)
        print("User = ", user)

        profile = get_user_info(access_token)
        print("Full profile = \n", json.dumps(profile, indent=2))

        profile_data = {
            "name": profile['name'],
            "email": profile['email'],
            "currency_preference": "USD",
            "profile_pic": profile['picture']
        }

        sql = SQLMachine()
        sql.insert("user_service_db", "user", profile_data)

        # return JSONResponse({"message": "Login successful", "user profile": profile})
        return HTMLResponse("Success!")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Authentication failed")

@app.get("/")
def get_root():
    return {"do it work"}
