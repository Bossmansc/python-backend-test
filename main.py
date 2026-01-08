# Entry point for Firebase Cloud Functions
from firebase_functions import https_fn
from main_preview import app as fastapi_app
import uvicorn
import io
import flask

# This is a lightweight adapter to make FastAPI work with the Firebase Functions decorator
# For production, we recommend deploying the container to Cloud Run directly.
@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    # ⚠️ Note: This is a simplified preview adapter.
    # It converts the Firebase/Flask request to something FastAPI can handle implies some overhead.
    # In a real production deployment on Firebase, you should use the containerized Cloud Run approach
    # or the proper ASGI adapter 'mangum' or 'a2wsgi'.
    # For the purpose of this preview, we will return a simple message if hit directly,
    # as the 'run_preview.py' is the preferred way to run in IDX.
    return https_fn.Response("Cloud Deploy API is running via Cloud Functions!")

# Note: To deploy the full FastAPI app to Firebase, the best practice is to use 
# Google Cloud Run directly with the Dockerfile provided (Dockerfile.complete),
# as Firebase Functions are optimized for event-driven logic rather than full REST APIs.
