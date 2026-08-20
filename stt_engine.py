"""
Bilingual Speech-to-Text Engine.
- English: OpenAI Whisper 'small' (local GPU inference)
- Kannada: vasista22/whisper-kannada-small (fine-tuned Whisper, direct model usage)

Uses WhisperProcessor + WhisperForConditionalGeneration directly
to avoid torchcodec/FFmpeg dependency issues on Windows.
"""

import time
import sys
import os

import torch
import numpy as np

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ──────────────────────────────────────
# English STT: OpenAI Whisper
# ──────────────────────────────────────
DEFAULT_WHISPER_MODEL = "tiny"
_whisper_cache = {}


def _get_whisper_model(model_size: str = DEFAULT_WHISPER_MODEL):
    """Load and cache the Whisper model for English."""
    if model_size not in _whisper_cache:
        import whisper
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔄 Loading Whisper '{model_size}' for English on {device}...")
        _whisper_cache[model_size] = whisper.load_model(model_size, device=device)
        print(f"✅ Whisper model loaded on {device}")
    return _whisper_cache[model_size]


def _english_stt(audio_path: str, model_size: str = DEFAULT_WHISPER_MODEL) -> dict:
    """Transcribe English audio using OpenAI Whisper."""
    model = _get_whisper_model(model_size)

    start_time = time.time()
    result = model.transcribe(audio_path, language="en", verbose=False)
    elapsed = time.time() - start_time

    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
        })

    audio_duration = segments[-1]["end"] if segments else 0

    return {
        "transcript": result["text"].strip(),
        "language": "en",
        "processing_time_seconds": round(elapsed, 2),
        "audio_duration_seconds": round(audio_duration, 2),
        "num_segments": len(segments),
        "segments": segments,
    }


# ──────────────────────────────────────
# Kannada STT: Fine-tuned Whisper
# (Direct model usage — no pipeline, no torchcodec)
# ──────────────────────────────────────
def _kannada_stt(audio_path: str, model_size: str = DEFAULT_WHISPER_MODEL) -> dict:
    """Transcribe Kannada audio using OpenAI Whisper (multilingual model for low RAM compatibility)."""
    model = _get_whisper_model(model_size)

    start_time = time.time()
    result = model.transcribe(audio_path, language="kn", verbose=False)
    elapsed = time.time() - start_time

    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
        })

    audio_duration = segments[-1]["end"] if segments else 0

    return {
        "transcript": result["text"].strip(),
        "language": "kn",
        "processing_time_seconds": round(elapsed, 2),
        "audio_duration_seconds": round(audio_duration, 2),
        "num_segments": len(segments),
        "segments": segments,
    }


# ──────────────────────────────────────
# Main entry point
# ──────────────────────────────────────

def speech_to_text(
    audio_path: str,
    language: str = "en",
    model_size: str = DEFAULT_WHISPER_MODEL,
) -> dict:
    """
    Transcribe an audio file to text.

    Args:
        audio_path: Path to audio file (MP3, WAV, FLAC, etc.)
        language: 'en' for English, 'kn' for Kannada
        model_size: Whisper model size (English only)

    Returns:
        dict with transcript, language, processing_time_seconds,
        audio_duration_seconds, num_segments, segments
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    import gc
    try:
        if language == "kn":
            return _kannada_stt(audio_path)
        else:
            return _english_stt(audio_path, model_size)
    finally:
        gc.collect()


if __name__ == "__main__":
    en_file = "output/test_en_female.mp3"
    if os.path.exists(en_file):
        result = speech_to_text(en_file, language="en")
        print(f"\n📝 English: {result['transcript'][:200]}")
        print(f"⏱️ {result['processing_time_seconds']}s")

    kn_file = "output/test_kn.wav"
    if os.path.exists(kn_file):
        result = speech_to_text(kn_file, language="kn")
        print(f"\n📝 Kannada: {result['transcript']}")
        print(f"⏱️ {result['processing_time_seconds']}s")
