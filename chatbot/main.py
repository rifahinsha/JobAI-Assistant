from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import JobChatbot
from email_cv import router as email_cv_router

app = FastAPI(title="Job Assistant Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email_cv_router)

sessions: dict[str, JobChatbot] = {}


def get_bot(session_id: str) -> JobChatbot:
    """Returns the chatbot for this session, creating one if it doesn't exist yet."""
    if session_id not in sessions:
        sessions[session_id] = JobChatbot()
    return sessions[session_id]


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@app.get("/")
def root():
    return {"status": "ok", "service": "Job Assistant Chatbot"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    bot = get_bot(req.session_id)
    reply = bot.chat(req.message)
    return ChatResponse(reply=reply, session_id=req.session_id)


@app.post("/reset")
def reset_chat(session_id: str = "default"):
    """Clear conversation history for a specific session."""
    bot = get_bot(session_id)
    bot.reset()
    return {"status": "cleared", "session_id": session_id}


@app.get("/history")
def get_history(session_id: str = "default"):
    """Debug endpoint — see memory for a specific session."""
    bot = get_bot(session_id)
    return {
        "session_id": session_id,
        "summary": bot.history_summary(),
        "messages": bot.memory.get_history()
    }