from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Important: Mount static AFTER the API routes
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
API_KEY_SID = os.getenv("TWILIO_API_KEY_SID")
API_KEY_SECRET = os.getenv("TWILIO_API_KEY_SECRET")

@app.get("/token")
async def get_token():
    try:
        token = AccessToken(ACCOUNT_SID, API_KEY_SID, API_KEY_SECRET, identity="friend_uk")
        voice_grant = VoiceGrant(incoming_allow=True)
        token.add_grant(voice_grant)
        return JSONResponse({"token": token.to_jwt()})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/voice")
async def voice_webhook(request: Request):
    response = VoiceResponse()
    dial = Dial()
    dial.client("friend_uk")
    response.append(dial)
    return HTMLResponse(str(response), media_type="application/xml")

# Serve static files (must be after routes)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)