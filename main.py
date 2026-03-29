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

@app.get("/token")
async def get_token():
    token = AccessToken(ACCOUNT_SID, API_KEY_SID, API_KEY_SECRET, identity="friend_uk")
    token.add_grant(VoiceGrant(incoming_allow=True))
    return JSONResponse({"token": token.to_jwt()})

@app.api_route("/voice", methods=["GET", "POST"])
async def voice_webhook(request: Request):
    try:
        # 1. Safely get data (use empty string as default to avoid NoneType errors)
        if request.method == "POST":
            form_data = await request.form()
        else:
            form_data = request.query_params

        to_number = str(form_data.get("To", ""))
        from_id = str(form_data.get("From", ""))

        response = VoiceResponse()

        # 2. Check if this is an Outgoing call from your SIP app
        # (It will have 'sip:' in the 'From' field)
        if from_id and "sip:" in from_id:
            # We split the number part out (e.g. sip:+1234@domain -> +1234)
            # Use a safe split to avoid errors
            target = to_number.split('@')[0].replace('sip:', '') if to_number else ""
            
            if target:
                dial = Dial(caller_id=TWILIO_NUMBER)
                dial.number(target)
                response.append(dial)
            else:
                response.say("Invalid destination number.")
        
        # 3. Handle Incoming calls to your Twilio number
        else:
            dial = Dial()
            # This rings your Linphone/Zoiper app
            dial.sip("sip:maisam2004@family-voip.sip.twilio.com")

            # 2. Rings your Web Browser (index.html)
            dial.client("friend_uk")
            response.append(dial)

        # Return the XML response
        return Response(content=str(response), media_type="application/xml")

    except Exception as e:
        # This will print the EXACT error in your Render logs
        logger.error(f"Error in voice_webhook: {e}")
        return Response(content=f"<Response><Say>Error: {str(e)}</Say></Response>", media_type="application/xml")
# --- Keep your existing Browser Phone endpoints below if you still want them ---



@app.get("/health")
async def health():
    return {"status": "ok"}

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())