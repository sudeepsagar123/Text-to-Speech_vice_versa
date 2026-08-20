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
DEFAULT_WHISPER_MODEL = "small"
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
_kn_model = None
_kn_processor = None

KN_MODEL_ID = "vasista22/whisper-kannada-small"


def _load_kannada_stt():
    """Load and cache the Kannada Whisper model + processor."""
    global _kn_model, _kn_processor
    if _kn_model is None:
        from transformers import WhisperProcessor, WhisperForConditionalGeneration

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔄 Loading Kannada STT ({KN_MODEL_ID}) on {device}...")

        _kn_processor = WhisperProcessor.from_pretrained(KN_MODEL_ID)
        _kn_model = WhisperForConditionalGeneration.from_pretrained(KN_MODEL_ID)
        _kn_model = _kn_model.to(device)
        _kn_model.eval()

        # Force Kannada language output
        _kn_model.config.forced_decoder_ids = _kn_processor.get_decoder_prompt_ids(
            language="kn", task="transcribe"
        )

        print(f"✅ Kannada STT model loaded on {device}")
    return _kn_model, _kn_processor


def _load_audio(audio_path: str, target_sr: int = 16000):
    """Load audio file as numpy array at target sample rate using soundfile/librosa."""
    try:
        import soundfile as sf
        audio, sr = sf.read(audio_path)
        # Convert stereo to mono
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        # Resample if needed
        if sr != target_sr:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
        return audio.astype(np.float32), target_sr
    except Exception:
        # Fallback to librosa (handles more formats)
        import librosa
        audio, sr = librosa.load(audio_path, sr=target_sr, mono=True)
        return audio, sr


def _kannada_stt(audio_path: str) -> dict:
    """Transcribe Kannada audio using fine-tuned Whisper (direct model call)."""
    model, processor = _load_kannada_stt()
    device = next(model.parameters()).device

    # Load audio ourselves (bypasses torchcodec entirely)
    audio_array, sr = _load_audio(audio_path, target_sr=16000)
    audio_duration = len(audio_array) / sr

    start_time = time.time()

    # Process audio into model input features
    input_features = processor(
        audio_array, sampling_rate=16000, return_tensors="pt"
    ).input_features.to(device)

    # Generate transcription
    with torch.no_grad():
        predicted_ids = model.generate(input_features)

    # Decode token IDs to text
    transcript = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

    elapsed = time.time() - start_time

    return {
        "transcript": transcript.strip(),
        "language": "kn",
        "processing_time_seconds": round(elapsed, 2),
        "audio_duration_seconds": round(audio_duration, 2),
        "num_segments": 1,
        "segments": [
            {
                "start": 0.0,
                "end": round(audio_duration, 2),
                "text": transcript.strip(),
            }
        ],
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

    if language == "kn":
        return _kannada_stt(audio_path)
    else:
        return _english_stt(audio_path, model_size)


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
