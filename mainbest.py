from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configure logging (optional, for debugging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
API_KEY_SID = os.getenv("TWILIO_API_KEY_SID")
API_KEY_SECRET = os.getenv("TWILIO_API_KEY_SECRET")

# Token TTL in seconds (1 hour)
TOKEN_TTL = 3600

@app.get("/token")
async def get_token():
    if not all([ACCOUNT_SID, API_KEY_SID, API_KEY_SECRET]):
        logger.error("Missing Twilio credentials in environment")
        return JSONResponse({"error": "Missing credentials"}, status_code=500)

    # Create access token with identity and TTL
    token = AccessToken(
        ACCOUNT_SID,
        API_KEY_SID,
        API_KEY_SECRET,
        identity="friend_uk",
        ttl=TOKEN_TTL
    )

    # Add Voice grant for incoming calls
    voice_grant = VoiceGrant(incoming_allow=True)
    token.add_grant(voice_grant)

    jwt_token = token.to_jwt()

    # Optional: decode and log expiration for debugging
    try:
        # Note: PyJWT may need to be installed; if not, skip.
        import jwt
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})
        exp_time = datetime.fromtimestamp(decoded['exp'])
        logger.info(f"Token generated, expires at {exp_time}")
    except Exception as e:
        logger.warning(f"Could not decode token for logging: {e}")

    return JSONResponse({"token": jwt_token})

@app.api_route("/voice", methods=["GET", "POST"])
async def voice_webhook(request: Request):
    response = VoiceResponse()
    dial = Dial()
    dial.client("friend_uk")
    response.append(dial)
    return HTMLResponse(str(response), media_type="application/xml")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)