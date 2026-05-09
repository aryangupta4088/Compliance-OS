from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.agents.aria import ARIAAgent
import json

router = APIRouter()

@router.websocket("/ws/aria/{session_id}")
async def websocket_aria(websocket: WebSocket, session_id: str):
    await websocket.accept()
    agent = ARIAAgent(session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            # Process and stream tokens back
            async for event in agent.process_message(payload["message"]):
                await websocket.send_json(event)
                
    except WebSocketDisconnect:
        print(f"WS disconnected: {session_id}")
