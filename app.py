"""
FastAPI backend for bilingual Text-to-Speech & Speech-to-Text application.
Supports English and Kannada (ಕನ್ನಡ).
"""

import os
import uuid
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from tts_engine import text_to_speech_async, VOICES
from stt_engine import speech_to_text

app = FastAPI(title="VoiceCraft AI", description="Bilingual TTS & STT — English + Kannada")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the main frontend page."""
    return FileResponse("static/index.html")


@app.get("/api/voices")
async def get_voices():
    """Return available voice options (English only)."""
    return {
        "voices": [
            {"key": "female", "name": "Neerja (Female)", "id": VOICES["female"]},
            {"key": "male", "name": "Prabhat (Male)", "id": VOICES["male"]},
        ]
    }


@app.post("/api/tts")
async def api_tts(
    text: str = Form(...),
    language: str = Form("en"),
    voice: str = Form("female"),
):
    """
    Convert text to speech.
    - language='en': English (Edge-TTS, MP3)
    - language='kn': Kannada (VITS, WAV)
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Set file extension and media type based on language
    if language == "kn":
        ext, media = ".wav", "audio/wav"
    else:
        ext, media = ".mp3", "audio/mpeg"

    filename = f"tts_{uuid.uuid4().hex[:8]}{ext}"
    output_path = os.path.join("output", filename)

    try:
        result = await text_to_speech_async(text, output_path, language=language, voice=voice)
        return FileResponse(
            output_path,
            media_type=media,
            filename=filename,
            headers={
                "X-Processing-Time": str(result["processing_time_seconds"]),
                "X-Text-Length": str(result["text_length"]),
                "X-Voice-Used": result["voice_used"],
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@app.post("/api/stt")
async def api_stt(
    audio: UploadFile = File(...),
    language: str = Form("en"),
):
    """
    Convert speech to text.
    - language='en': English (Whisper)
    - language='kn': Kannada (IndicConformer)
    """
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio file provided")

    ext = os.path.splitext(audio.filename)[1] or ".mp3"
    temp_filename = f"stt_{uuid.uuid4().hex[:8]}{ext}"
    temp_path = os.path.join("output", temp_filename)

    try:
        content = await audio.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, speech_to_text, temp_path, language)

        return {
            "transcript": result["transcript"],
            "language": result["language"],
            "processing_time_seconds": result["processing_time_seconds"],
            "audio_duration_seconds": result["audio_duration_seconds"],
            "num_segments": result["num_segments"],
            "segments": result["segments"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    print("\n🚀 Starting VoiceCraft AI Server (English + Kannada)...")
    print(f"📍 Open http://localhost:{port} in your browser\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
