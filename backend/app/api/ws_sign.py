import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.sign_service import SignService

router = APIRouter()
sign_service = SignService()

@router.websocket("/ws/sign")
async def websocket_sign_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time sign language classification.
    Receives coordinate landmark sequences and returns predicted sign labels.
    """
    await websocket.accept()
    print("Sign recognition WebSocket connection established.")
    
    # Store sliding window of frames for continuous inference
    landmark_history = []
    
    try:
        while True:
            # Receive frame landmark data
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            landmarks = payload.get("landmarks")
            if not landmarks:
                continue

            # landmarks is a list of floats (e.g. 126 features)
            landmark_history.append(landmarks)
            
            # Maintain a sliding window of 30 frames
            if len(landmark_history) > 30:
                landmark_history.pop(0)

            # Perform prediction once we have enough frames
            # To increase responsiveness, we can classify every 5-10 frames (sliding overlap)
            if len(landmark_history) >= 15:
                label, confidence = sign_service.predict(landmark_history)
                
                # Only broadcast prediction if it matches our confidence budget (e.g. >= 70%)
                if confidence >= 0.70:
                    response = {
                        "type": "prediction",
                        "sign": label,
                        "confidence": confidence,
                        "timestamp": payload.get("timestamp")
                    }
                    await websocket.send_text(json.dumps(response))
                    
    except WebSocketDisconnect:
        print("Sign recognition WebSocket disconnected.")
    except Exception as e:
        print(f"Error in sign WebSocket session: {e}")
        try:
            await websocket.close()
        except:
            pass
