from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")
# API routes first
@app.post("/voice")
async def voice_webhook(request: Request):
    """Telnyx sends inbound calls here"""
    form = await request.form()
    
    # Simple TeXML to answer and bridge to browser client
    texml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Answer/>
    <Dial>
        <Client>friend_uk</Client>
    </Dial>
</Response>'''
    
    return HTMLResponse(texml, media_type="application/xml")

# Serve the frontend (must be after routes)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)