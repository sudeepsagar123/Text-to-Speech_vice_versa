"""
Bilingual Text-to-Speech Engine.
- English: Edge-TTS (Microsoft neural TTS, async, MP3 output)
- Kannada: facebook/mms-tts-kan (VITS model, local inference, WAV output)
"""

import asyncio
import os
import time
import re
import numpy as np

import edge_tts

# ── English voices (Edge-TTS) ──
VOICES = {
    "female": "en-IN-NeerjaNeural",
    "male": "en-IN-PrabhatNeural",
}
DEFAULT_VOICE = "female"

# ── Kannada VITS model (lazy-loaded) ──
_kn_model = None
_kn_tokenizer = None


def _load_kannada_model():
    """Load and cache the facebook/mms-tts-kan VITS model."""
    global _kn_model, _kn_tokenizer
    if _kn_model is None:
        import torch
        from transformers import VitsModel, AutoTokenizer

        print("🔄 Loading Kannada TTS model (facebook/mms-tts-kan)...")
        _kn_tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-kan")
        _kn_model = VitsModel.from_pretrained("facebook/mms-tts-kan")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        _kn_model = _kn_model.to(device)
        _kn_model.eval()
        print(f"✅ Kannada TTS model loaded on {device}")
    return _kn_model, _kn_tokenizer


def _split_kannada_sentences(text: str) -> list[str]:
    """Split Kannada text into sentences on '|', '।', '.', or newlines."""
    parts = re.split(r'[।\.\|\n]+', text)
    return [p.strip() for p in parts if p.strip()]


def _kannada_tts(text: str, output_path: str) -> dict:
    """Generate Kannada speech using facebook/mms-tts-kan."""
    import torch
    import scipy.io.wavfile as wavfile

    model, tokenizer = _load_kannada_model()
    device = next(model.parameters()).device

    start_time = time.time()

    sentences = _split_kannada_sentences(text)
    if not sentences:
        sentences = [text]

    all_waveforms = []
    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors="pt").to(device)
        with torch.no_grad():
            output = model(**inputs)
        waveform = output.waveform.squeeze().cpu().numpy()
        all_waveforms.append(waveform)

    # Concatenate with small silence between sentences
    sample_rate = model.config.sampling_rate
    silence = np.zeros(int(sample_rate * 0.3), dtype=np.float32)

    final_parts = []
    for i, wf in enumerate(all_waveforms):
        final_parts.append(wf)
        if i < len(all_waveforms) - 1:
            final_parts.append(silence)

    final_waveform = np.concatenate(final_parts)

    # Normalize to prevent clipping
    peak = np.max(np.abs(final_waveform))
    if peak > 0:
        final_waveform = final_waveform / peak * 0.95

    # Save as 16-bit WAV
    int16_audio = (final_waveform * 32767).astype(np.int16)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    wavfile.write(output_path, rate=sample_rate, data=int16_audio)

    elapsed = time.time() - start_time
    file_size = os.path.getsize(output_path)

    return {
        "output_path": output_path,
        "processing_time_seconds": round(elapsed, 2),
        "voice_used": "mms-tts-kan (Kannada VITS)",
        "text_length": len(text),
        "file_size_bytes": file_size,
    }


async def text_to_speech_async(
    text: str,
    output_path: str,
    language: str = "en",
    voice: str = DEFAULT_VOICE,
) -> dict:
    """
    Convert text to speech.

    Args:
        text: Input text (any length)
        output_path: Path to save the output audio file
        language: 'en' for English (Edge-TTS), 'kn' for Kannada (VITS)
        voice: Voice key for English ('female' or 'male'); ignored for Kannada

    Returns:
        dict with output_path, processing_time_seconds, voice_used, text_length, file_size_bytes
    """
    if language == "kn":
        # Run VITS inference in thread pool (CPU/GPU-bound)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _kannada_tts, text, output_path)
    else:
        # English: use Edge-TTS (async I/O)
        voice_name = VOICES.get(voice, voice)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        start_time = time.time()
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(output_path)
        elapsed = time.time() - start_time

        return {
            "output_path": output_path,
            "processing_time_seconds": round(elapsed, 2),
            "voice_used": voice_name,
            "text_length": len(text),
            "file_size_bytes": os.path.getsize(output_path),
        }


def text_to_speech(
    text: str,
    output_path: str,
    language: str = "en",
    voice: str = DEFAULT_VOICE,
) -> dict:
    """Synchronous wrapper for text_to_speech_async."""
    return asyncio.run(text_to_speech_async(text, output_path, language, voice))


if __name__ == "__main__":
    # Quick test — English
    en_text = "Hello! This is a test of the Indian English text to speech engine."
    result = text_to_speech(en_text, "output/test_en.mp3", language="en", voice="female")
    print(f"✅ English TTS: {result}")

    # Quick test — Kannada
    kn_text = "ನಮಸ್ಕಾರ! ಇದು ಕನ್ನಡ ಪಠ್ಯದಿಂದ ಧ್ವನಿಗೆ ಪರಿವರ್ತನೆಯ ಪರೀಕ್ಷೆ."
    result = text_to_speech(kn_text, "output/test_kn.wav", language="kn")
    print(f"✅ Kannada TTS: {result}")
