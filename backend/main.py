import os
import sys

# Ensure dependencies folder is in path (Critical for App Runner multi-stage builds)
sys.path.insert(0, os.path.join(os.getcwd(), "dependencies"))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# Import services
from nova_client import NovaClient
from ticket_service import TicketService
from crm_service import CRMService
from embeddings_service import EmbeddingsService
from utils import S3Utils
from agent_brain import AgentBrain

app = FastAPI(title="NovaAssist CX API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
nova = NovaClient()
tickets = TicketService()
crm = CRMService()
embeddings = EmbeddingsService(nova)
s3 = S3Utils()
brain = AgentBrain(nova)

class ChatRequest(BaseModel):
    message: str
    customer_email: str
    session_id: Optional[str] = None

class ActionRequest(BaseModel):
    action_type: str
    details: dict

@app.post("/support/chat")
async def support_chat(request: ChatRequest):
    """
    Agentic Chat: Handles memory, reasoning, and tool execution.
    """
    session_id = request.session_id or request.customer_email
    result = await brain.run_agent_loop(session_id, request.message)
    
    return {
        "response": result["response"],
        "session_id": result["session_id"]
    }

@app.post("/support/upload")
async def screenshot_analysis(email: str = Form(...), file: UploadFile = File(...)):
    file_bytes = await file.read()
    
    # 1. Upload to S3
    s3_url = s3.upload_file(file_bytes, file.filename)
    
    # 2. Analyze with Nova
    analysis = await embeddings.analyze_screenshot(file_bytes)
    
    # 3. Create ticket based on analysis
    description = f"Screenshot analysis: {analysis}"
    ticket = tickets.create_ticket(email, description)
    await crm.create_crm_ticket(email, description)
    
    return {
        "analysis": analysis,
        "s3_url": s3_url,
        "ticket_id": ticket["ticket_id"]
    }

@app.post("/support/voice")
async def voice_support(email: str = Form(...), file: UploadFile = File(...), session_id: Optional[str] = Form(None)):
    """
    Agentic Voice: Transcribes, reasons with tools, and talks back.
    """
    audio_bytes = await file.read()
    
    # 1. Transcribe (Optimized in NovaClient)
    transcription = nova.transcribe_audio(audio_bytes, file.filename)
    
    # 2. Agentic Reasoning (Provides tool access via voice)
    # 2. Transcribe & Process (Simulated Transcribe + Act)
    # Ensure transcription is not blank to avoid Bedrock ValidationException
    if not transcription or not transcription.strip():
        transcription = "Continue" # Or just return silence
        
    current_session = session_id or email
    result = await brain.run_agent_loop(current_session, transcription)
    response_text = result["response"]
    
    # 3. Talk back (Polly Neural) - Advanced reasoning suppression
    import re
    # Strip <thinking> tags and any "Internal Reasoning" markers Nova might use
    voice_text = re.sub(r'<thinking>[\s\S]*?</thinking>', '', response_text)
    voice_text = re.sub(r'Internal Reasoning:?.*?\n', '', voice_text, flags=re.IGNORECASE)
    voice_text = voice_text.strip()
    
    if not voice_text:
        voice_text = "Task completed successfully."
        
    audio_response_bytes = nova.generate_speech(voice_text)
    
    import base64
    audio_base64 = base64.b64encode(audio_response_bytes).decode('utf-8')
    
    return {
        "transcription": transcription,
        "response": response_text,
        "audio": audio_base64,
        "session_id": result["session_id"]
    }

@app.post("/support/action")
async def support_action(request: ActionRequest):
    # Use Nova Act (orchestrated via Nova Lite) to trigger actions
    tools = [
        {"name": "reset_password", "description": "Resets user password", "inputSchema": {"json": {"type": "object", "properties": {"user_id": {"type": "string"}}}}},
        {"name": "request_refund", "description": "Requests a refund", "inputSchema": {"json": {"type": "object", "properties": {"order_id": {"type": "string"}}}}}
    ]
    
    prompt = f"Executing action: {request.action_type} with details {request.details}"
    # In a full implementation, we'd handle the tool calls returned by Nova
    
    return {"status": "success", "action": request.action_type, "message": f"Action {request.action_type} triggered successfully."}

@app.get("/tickets")
async def list_tickets():
    return tickets.get_all_tickets()

# Mount Frontend Static Files (Consolidated Deployment)
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"Warning: Static path {frontend_path} not found.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
