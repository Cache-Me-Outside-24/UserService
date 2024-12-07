from fastapi import FastAPI, Depends, HTTPException
from services.sql_comands import SQLMachine
from pydantic import BaseModel
from starlette.responses import HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Define a Pydantic model for the request body
class UserSignUp(BaseModel):
    user_email: str
    username: str
    uid: str


# Default profile picture link
DEFAULT_PROFILE_PIC = "https://example.com/default-profile-pic.png"
DEFAULT_CURRENCY = "USD"


@app.post("/sign-up")
async def sign_up(user: UserSignUp):
    """
    Sign up endpoint that takes user_email and username,
    inserts them into the SQL database with default values for profile_pic and currency_preference.
    """
    # Data to insert into the database
    profile_data = {
        "name": user.username,
        "email": user.user_email,
        "id": user.uid,
        "currency_preference": DEFAULT_CURRENCY,
        "profile_pic": DEFAULT_PROFILE_PIC,
    }

    try:
        # Insert into the SQL database
        sql = SQLMachine()
        sql.insert("user_service_db", "users", profile_data)
        return HTMLResponse("User successfully signed up!")
    except Exception as e:
        print(f"Error inserting user into the database: {e}")
        raise HTTPException(status_code=500, detail="Failed to sign up the user")


@app.get("/")
def get_root():
    return {"message": "Service is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
