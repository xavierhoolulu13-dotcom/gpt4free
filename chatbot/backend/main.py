import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
from datetime import datetime

from sheets_backend import GoogleSheetsBackend, initialize_default_workflows
from intent_router import IntentRouter
from chatbot_agent import ChatbotAgent

# Initialize
app = FastAPI(title="n8n Chatbot API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
SHEETS_ID = os.getenv("SHEETS_ID", "your-sheets-id-here")
CREDENTIALS_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "credentials.json")

# Initialize components
try:
    sheets_backend = GoogleSheetsBackend(SHEETS_ID, CREDENTIALS_PATH)
    initialize_default_workflows(sheets_backend)
except Exception as e:
    print(f"Warning: Could not initialize Google Sheets backend: {e}")
    print("Using mock backend for testing")
    sheets_backend = None

intent_router = IntentRouter()
agent = ChatbotAgent(sheets_backend, intent_router) if sheets_backend else None

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    workflow: str
    confidence: str
    keywords_matched: list
    response_time: str
    timestamp: str

# Routes
@app.get("/")
async def root():
    """API health check."""
    return {
        "status": "ok",
        "service": "n8n Chatbot API",
        "version": "1.0.0",
        "sheets_connected": sheets_backend is not None
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """One-shot chat endpoint."""
    if not agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    session_id = request.session_id or str(uuid.uuid4())
    user_id = request.user_id or "anonymous"
    
    result = await agent.process_message(
        message=request.message,
        session_id=session_id,
        user_id=user_id
    )
    
    return ChatResponse(
        response=result['response'],
        intent=result['intent'],
        workflow=result['workflow'],
        confidence=result['confidence'],
        keywords_matched=result['keywords_matched'],
        response_time=result['response_time'],
        timestamp=datetime.now().isoformat()
    )

@app.get("/stream")
async def stream(message: str, session_id: Optional[str] = None, user_id: Optional[str] = None):
    """Server-Sent Events streaming endpoint."""
    if not agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    session_id = session_id or str(uuid.uuid4())
    user_id = user_id or "anonymous"
    
    async def event_generator():
        async for chunk in agent.stream_response(
            message=message,
            session_id=session_id,
            user_id=user_id
        ):
            yield f"data: {json.dumps({'chunk': chunk, 'session_id': session_id})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/history")
async def get_history(session_id: str):
    """Get conversation history for a session."""
    if not agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    history = agent.get_session_history(session_id)
    return {"session_id": session_id, "messages": history}

@app.post("/clear")
async def clear_session(session_id: str):
    """Clear session history."""
    if agent:
        agent.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}

@app.get("/workflows")
async def get_workflows():
    """Get all available workflows."""
    if not sheets_backend:
        return {"workflows": []}
    return {"workflows": sheets_backend.get_workflows()}

@app.get("/agents")
async def get_agents(workflow_id: Optional[str] = None):
    """Get agents, optionally filtered by workflow."""
    if not sheets_backend:
        return {"agents": []}
    return {"agents": sheets_backend.get_agents(workflow_id)}

@app.post("/refresh")
async def refresh():
    """Refresh workflows and agents from Google Sheets."""
    if not sheets_backend:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Re-initialize default workflows
    initialize_default_workflows(sheets_backend)
    
    return {
        "status": "refreshed",
        "workflows": len(sheets_backend.get_workflows()),
        "agents": len(sheets_backend.get_agents())
    }

@app.get("/routing-info")
async def get_routing_info(message: str):
    """Debug endpoint: Show how a message would be routed."""
    if not sheets_backend:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    routing_rules = sheets_backend.get_routing_rules()
    decision = intent_router.route(message, routing_rules)
    explanation = intent_router.explain_routing(message, decision)
    
    return explanation

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)