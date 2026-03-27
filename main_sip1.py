from fastapi.responses import Response # Add this to your imports
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


# You should add your purchased Twilio number to your .env file
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER") 
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
    # Get the form data from Twilio's request
    form_data = await request.form()
    to_number = form_data.get("To")
    from_sip = form_data.get("From")

    response = VoiceResponse()

    # SCENARIO 1: OUTGOING CALL FROM YOUR VOIP APP
    # If the call comes from your SIP domain, it's you trying to call out.
    if from_sip and "sip:" in from_sip:
        # Extract the destination number from the SIP URI
        # e.g., sip:+1234567890@family-voip.sip.twilio.com -> +1234567890
        target = to_number.split('@')[0].replace('sip:', '')
        
        dial = Dial(caller_id=TWILIO_NUMBER) # Use your Twilio number as Caller ID
        dial.number(target)
        response.append(dial)
    
    # SCENARIO 2: INCOMING CALL TO YOUR TWILIO NUMBER
    # Someone is calling your Twilio number; we route it to your registered SIP phone.
    else:
        dial = Dial()
        # Direct the call to your specific SIP endpoint
        dial.sip("sip:maisam2004@gmail.com@family-voip.sip.twilio.com")
        response.append(dial)

    return Response(content=str(response), media_type="application/xml")

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