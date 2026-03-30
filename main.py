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

# Configuration from .env — .strip() handles spaces around = in Render env vars
TWILIO_NUMBER = (os.getenv("TWILIO_NUMBER") or "").strip()
ACCOUNT_SID   = (os.getenv("TWILIO_ACCOUNT_SID") or "").strip()
API_KEY_SID    = (os.getenv("TWILIO_API_KEY_SID") or "").strip()
API_KEY_SECRET = (os.getenv("TWILIO_API_KEY_SECRET") or "").strip()
IDENTITY       = (os.getenv("IDENTITY") or "browser_client").strip()
SIP_INFO       = (os.getenv("SIP_INFO") or "").strip()


@app.get("/token")
async def get_token():
    token = AccessToken(ACCOUNT_SID, API_KEY_SID, API_KEY_SECRET, identity=IDENTITY)
    token.add_grant(VoiceGrant(incoming_allow=True))
    return JSONResponse({"token": token.to_jwt()})


@app.api_route("/voice", methods=["GET", "POST"])
async def voice_webhook(request: Request):
    try:
        if request.method == "POST":
            form_data = await request.form()
        else:
            form_data = request.query_params

        to_number = str(form_data.get("To", ""))
        from_id   = str(form_data.get("From", ""))

        response = VoiceResponse()

        # Outgoing call originating from SIP client
        if from_id and "sip:" in from_id:
            target = to_number.split('@')[0].replace('sip:', '') if to_number else ""
            if target:
                dial = Dial(caller_id=TWILIO_NUMBER)
                dial.number(target)
                response.append(dial)
            else:
                response.say("Invalid destination number.")

        # Incoming call to your Twilio number
        else:
            dial = Dial()
            # Ring SIP client only if SIP_INFO is configured
            if SIP_INFO:
                dial.sip(SIP_INFO)
            # Ring the browser client
            dial.client(IDENTITY)
            response.append(dial)

        return Response(content=str(response), media_type="application/xml")

    except Exception as e:
        logger.error(f"Error in voice_webhook: {e}")
        return Response(
            content=f"<Response><Say>Server error: {str(e)}</Say></Response>",
            media_type="application/xml"
        )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "identity": IDENTITY,
        "twilio_number": TWILIO_NUMBER,
        "sip_configured": bool(SIP_INFO)
    }


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def serve_index():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/sw.js")
async def service_worker():
    with open("static/sw.js") as f:
        return Response(content=f.read(), media_type="application/javascript")
