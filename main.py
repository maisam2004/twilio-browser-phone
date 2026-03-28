import os
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuration from .env
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER") 
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
API_KEY_SID = os.getenv("TWILIO_API_KEY_SID")
API_KEY_SECRET = os.getenv("TWILIO_API_KEY_SECRET")

@app.api_route("/voice", methods=["GET", "POST"])
async def voice_webhook(request: Request):
    form_data = await request.form()
    to_number = form_data.get("To", "")
    from_id = form_data.get("From", "")

    response = VoiceResponse()

    # SCENARIO 1: OUTGOING (Call made FROM your Android app)
    if "sip:" in from_id:
        # Clean the number (e.g., sip:+44123@domain -> +44123)
        target = to_number.split('@')[0].replace('sip:', '')
        
        # Dial the real phone number using your Twilio number as Caller ID
        dial = Dial(caller_id=TWILIO_NUMBER)
        dial.number(target)
        response.append(dial)
        logger.info(f"Outgoing SIP call to {target}")
    
    # SCENARIO 2: INCOMING (Someone calls your Twilio number)
    else:
        dial = Dial()
        # Ring your SIP phone
        dial.sip("sip:maisam2004@gmail.com@family-voip.sip.twilio.com")
        response.append(dial)
        logger.info("Incoming call routed to SIP app")

    return Response(content=str(response), media_type="application/xml")

# --- Keep your existing Browser Phone endpoints below if you still want them ---

@app.get("/token")
async def get_token():
    token = AccessToken(ACCOUNT_SID, API_KEY_SID, API_KEY_SECRET, identity="friend_uk")
    token.add_grant(VoiceGrant(incoming_allow=True))
    return JSONResponse({"token": token.to_jwt()})

@app.get("/health")
async def health():
    return {"status": "ok"}

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())