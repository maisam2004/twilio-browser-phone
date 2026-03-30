# 📞 Twilio Browser Phone

> **A Progressive Web App (PWA) browser-based softphone — make and receive real phone calls directly from your browser using Twilio Voice, powered by FastAPI.**

![PWA Ready](https://img.shields.io/badge/PWA-Ready-blueviolet?logo=googlechrome)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![Twilio](https://img.shields.io/badge/Powered%20by-Twilio-F22F46?logo=twilio)

---

## 📖 Overview

**Twilio Browser Phone** is a lightweight browser-based softphone that lets you:

- 📲 **Make outgoing calls** to real phone numbers from your browser
- 📥 **Receive incoming calls** to your Twilio number directly in the browser
- 📡 **Route calls to SIP clients** (e.g. Linphone, Zoiper) simultaneously
- 📱 **Install as a PWA** on Android, iOS, or desktop for a native app feel

The backend is a minimal **FastAPI** server that issues Twilio Access Tokens and handles TwiML voice webhooks.

---

## ✨ Features

- 🔑 **Twilio Access Token generation** — secure JWT tokens for browser SDK auth
- 📞 **Outgoing calls** — dial any phone number from the browser UI
- 📲 **Incoming calls** — receive calls via Twilio Voice SDK in the browser
- 🔀 **SIP + Browser simultaneous ringing** — calls ring both your SIP client and browser at once
- 📱 **PWA installable** — `manifest.json` + `sw.js` service worker for offline support and home screen install
- 🧩 **Telnyx variant** — includes an alternative `main_telnyx.py` / `index_telnyx.html` for Telnyx integration
- ⚡ **FastAPI** — fast, async Python backend
- 🏥 **Health check endpoint** — `/health` for uptime monitoring

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11+ |
| Voice API | Twilio Voice SDK (JS) + TwiML |
| Alternative | Telnyx WebRTC |
| Frontend | Vanilla HTML/CSS/JS, Twilio `twilio.min.js` |
| PWA | `manifest.json` + `sw.js` Service Worker |
| Auth | Twilio Access Token (JWT) |

---

## 📁 Project Structure

```
twilio-browser-phone/
├── main.py                # FastAPI app — token endpoint + voice webhook (primary)
├── main_main.py           # Alternative main entry point
├── mainbest.py            # Refined version of the app
├── main_telnyx.py         # Telnyx variant backend
├── requirements.txt       # Python dependencies
├── explain.txt            # Developer notes
├── .gitignore
└── static/
    ├── index.html         # Main PWA browser phone UI
    ├── index_main.html    # Alternative UI version
    ├── index_telnyx.html  # Telnyx variant UI
    ├── manifest.json      # PWA manifest
    ├── sw.js              # Service Worker (offline + installable)
    ├── twilio.min.js      # Twilio Voice JS SDK (bundled)
    ├── icon-192.png       # PWA icon (192x192)
    └── icon-512.png       # PWA icon (512x512)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- A [Twilio account](https://www.twilio.com/) with:
  - A Twilio Phone Number
  - An API Key SID + Secret
  - Account SID
- `ngrok` or a public server URL for webhooks during local development

### 1. Clone the repository

```bash
git clone https://github.com/maisam2004/twilio-browser-phone.git
cd twilio-browser-phone
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_KEY_SID=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_KEY_SECRET=your_api_key_secret
TWILIO_NUMBER=+44xxxxxxxxxx
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` in your browser.

---

## 🌐 Twilio Webhook Configuration

For Twilio to route incoming calls to your server, you must set your Twilio Voice webhook URL.

**During local development**, expose your server with ngrok:

```bash
ngrok http 8000
```

Then in the [Twilio Console](https://console.twilio.com/):

1. Go to **Phone Numbers → Manage → Active Numbers**
2. Select your number
3. Under **Voice & Fax → A Call Comes In**, set:
   ```
   https://your-ngrok-url.ngrok.io/voice
   ```
4. Set the HTTP method to **POST**

---

## 📱 PWA — Install on Your Device

The app is fully PWA-ready with a service worker and web manifest.

| File | Purpose |
|---|---|
| `static/manifest.json` | App name, icons, theme colour, display mode |
| `static/sw.js` | Service Worker — caches assets for offline use |
| `static/icon-192.png` | App icon for Android home screen |
| `static/icon-512.png` | App icon for splash screen |

### How to install:

- **Android / Chrome**: Tap the **"Add to Home Screen"** banner or use the browser menu
- **iOS / Safari**: Tap the **Share** icon → **"Add to Home Screen"**
- **Desktop / Chrome**: Click the **install icon** (⊕) in the address bar

> ✅ Once installed, the app works like a native phone app — opens full screen, no browser chrome.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serve the browser phone UI (`index.html`) |
| `GET` | `/token` | Generate a Twilio Access Token for the browser SDK |
| `GET / POST` | `/voice` | TwiML webhook — handles inbound/outbound call routing |
| `GET` | `/sw.js` | Serve the PWA service worker |
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |

---

## 📞 How Calls Work

### Incoming Call Flow

```
Caller dials your Twilio number
        ↓
Twilio hits POST /voice
        ↓
FastAPI returns TwiML → Dials both:
   ├── SIP client (Linphone / Zoiper)
   └── Browser client ("friend_uk" identity)
        ↓
First to answer gets the call
```

### Outgoing Call Flow

```
Browser dials a number via Twilio SDK
        ↓
Twilio hits POST /voice with From=sip:...
        ↓
FastAPI detects SIP origin → Dials target phone number
        ↓
Call connects through your Twilio number as caller ID
```

---

## 🧩 Telnyx Variant

The repo also includes a Telnyx WebRTC alternative:

- **Backend**: `main_telnyx.py`
- **Frontend**: `static/index_telnyx.html`

To run the Telnyx version:

```bash
uvicorn main_telnyx:app --reload
```

You'll need a Telnyx account and API credentials.

---

## 📦 Dependencies

See `requirements.txt`. Key packages:

- `fastapi` — web framework
- `uvicorn` — ASGI server
- `twilio` — Twilio helper library (Access Token + TwiML)
- `python-dotenv` — environment variable loading

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 👤 Author

**Maisam** — [@maisam2004](https://github.com/maisam2004)

---

*Built with ❤️ using FastAPI + Twilio Voice SDK + PWA*
