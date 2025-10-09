# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import OpenAI

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# OpenAI client using LionX_API_KEY env var
OPENAI_API_KEY = os.getenv("LionX_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing LionX_API_KEY environment variable")

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4o-mini"  # choose model you prefer

SYSTEM_PROMPT = (
    "You are LionMind-GPT: a helpful, polite chatbot prototype. "
    "Answer succinctly and help the user debug or explore the LionMind project. "
    "Never reveal any real API keys or secrets. Keep responses short (one paragraph) unless the user asks for more detail."
)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Render empty chat UI (stateless)
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, message: str = Form(...)):
    message_text = (message or "").strip()
    if not message_text:
        reply = "Please type a question or prompt."
        return templates.TemplateResponse("index.html", {"request": request, "message": message_text, "reply": reply})

    # Minimal safety: enforce small word limit
    if len(message_text.split()) > 80:
        reply = "Please keep messages under 80 words."
        return templates.TemplateResponse("index.html", {"request": request, "message": message_text, "reply": reply})

    # Build prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message_text}
    ]

    try:
        # Use the new OpenAI Python client
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=300,
        )
        # access the assistant reply
        reply = resp.choices[0].message.content
    except Exception as e:
        reply = f"Error contacting model: {e}"

    return templates.TemplateResponse("index.html", {"request": request, "message": message_text, "reply": reply})
