import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.speech_service import SpeechService

router = APIRouter()
speech_service = SpeechService()


@router.websocket("/ws/speech")
async def websocket_speech_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for speech recognition (transcription).
    Receives raw PCM binary audio chunks and streams transcribed captions.
    """
    await websocket.accept()
    print("Speech recognition WebSocket connection established.")

    # Store audio chunks for transcript context window
    audio_buffer = bytearray()

    try:
        while True:
            # Receive binary PCM audio chunks (16kHz mono 16-bit)
            message = await websocket.receive()

            if "bytes" in message:
                chunk = message["bytes"]
                audio_buffer.extend(chunk)

                # Transcribe once we accumulate sufficient audio (e.g. ~1 second of audio)
                # 1 second of 16kHz 16-bit mono is 32000 bytes
                if len(audio_buffer) >= 32000:
                    text = await speech_service.transcribe_chunk(bytes(audio_buffer))

                    if text:
                        response = {
                            "type": "final",
                            "text": text,
                            "timestamp": message.get("timestamp", 0),
                        }
                        await websocket.send_text(json.dumps(response))

                    # Clear buffer
                    audio_buffer.clear()
            else:
                # Handle text frames if sent (e.g. metadata or control commands)
                pass

    except WebSocketDisconnect:
        print("Speech recognition WebSocket disconnected.")
    except Exception as e:
        print(f"Error in speech WebSocket session: {e}")
        try:
            await websocket.close()
        except Exception:
            pass
