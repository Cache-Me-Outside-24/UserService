from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, Form
from services.sql_comands import SQLMachine
from pydantic import BaseModel
from starlette.responses import HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage

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
DEFAULT_PROFILE_PIC = "/assets/images/default_profile.png"
DEFAULT_CURRENCY = "USD"
# GCP Bucket Configuration
BUCKET_NAME = "cache-me-outside"


def upload_to_gcp(file: UploadFile, destination_blob_name: str) -> str:
    """
    Uploads a file to GCP bucket and returns the public URI.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)

        # Upload the file
        blob.upload_from_file(file.file)

        # Make the file publicly accessible
        blob.make_public()

        return blob.public_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")


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
    microservice_info = {
        "name": "User Service",
        "description": "Manages user management and detail retrieval",
    }
    return microservice_info


@app.get("/email-exists")
async def email_exists(
    email: str = Query(..., description="Email to check in the database")
):
    """
    Check if a given email exists in the database.
    """
    sql = SQLMachine()
    result = sql.select("user_service_db", "users", {"email": email})
    return {"exists": bool(result)}


@app.get("/user-info")
async def get_user_info(
    user_id: str = Query(..., description="The user ID for which to fetch info")
):
    """
    API endpoint to get user information by user ID.
    """
    schema = "user_service_db"  # Replace with your actual schema name
    table = "users"  # Replace with your actual table name

    sql = SQLMachine()
    result = sql.select_user_info(schema, table, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    # Map result to meaningful keys
    return {"username": result[0], "email": result[1], "profile-pic": result[2]}


@app.post("/upload-photo")
async def upload_profile_photo(file: UploadFile, user_id: str = Form(...)):
    """
    Uploads a profile photo to the GCP bucket and renames it to {user_id}_photo.ext.
    """
    try:
        file_extension = file.filename.split(".")[-1]
        destination_blob_name = f"user/{user_id}_photo.{file_extension}"

        # Upload to GCP bucket
        public_url = upload_to_gcp(file, destination_blob_name)
        return {"uri": public_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")


@app.post("/update-profile")
async def update_profile_info(user_id: str, username: str, profile_photo: str = None):
    """
    Updates the user's profile information in the SQL database.
    """
    try:
        sql = SQLMachine()
        sql.update(
            "user_service_db",
            "users",
            {"name": username, "profile_pic": profile_photo},
            {"id": user_id},
        )
        return {"message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update profile: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)
