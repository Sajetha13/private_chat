from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
from datetime import datetime

app = FastAPI()

# Setup templates and static folder
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup
conn = sqlite3.connect("chat.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    text TEXT,
    timestamp TEXT
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY
)
''')
conn.commit()

# Landing page for username input
@app.get("/")
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.post("/create_user")
def create_user(username: str = Form(...)):
    username = username.strip()
    if not username:
        return RedirectResponse("/", status_code=303)
    # Insert user if not exists
    c.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
    conn.commit()
    return RedirectResponse(f"/chat/{username}", status_code=303)

# Chat page
@app.get("/chat/{username}")
def chat_page(request: Request, username: str):
    # Check if user exists
    c.execute("SELECT username FROM users WHERE username = ?", (username,))
    if not c.fetchone():
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("chat.html", {"request": request, "username": username})

# Send message
@app.post("/messages")
def send_message(sender: str = Form(...), receiver: str = Form(...), text: str = Form(...)):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO messages (sender, receiver, text, timestamp) VALUES (?, ?, ?, ?)",
              (sender, receiver, text, timestamp))
    conn.commit()
    return {"status": "success"}

# Get messages between two users
@app.get("/messages")
def get_messages(sender: str, receiver: str):
    c.execute("""
        SELECT sender, text, timestamp FROM messages
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY id ASC
    """, (sender, receiver, receiver, sender))
    msgs = c.fetchall()
    return {"messages": [{"sender": m[0], "text": m[1], "timestamp": m[2]} for m in msgs]}
