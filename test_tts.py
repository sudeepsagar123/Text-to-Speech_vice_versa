"""
Bilingual TTS Test — English + Kannada.
Tests both Edge-TTS (English) and MMS-TTS-KAN (Kannada).
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts_engine import text_to_speech

# English test text
EN_TEXT = """
Artificial intelligence has become one of the most transformative technologies of the twenty-first century.
From virtual assistants that respond to voice commands to sophisticated algorithms that drive autonomous vehicles,
AI is no longer a concept confined to science fiction. It is a living, breathing reality.
"""

# Kannada test text
KN_TEXT = """
ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಇಂದಿನ ಯುಗದ ಅತ್ಯಂತ ಪ್ರಮುಖ ತಂತ್ರಜ್ಞಾನಗಳಲ್ಲಿ ಒಂದಾಗಿದೆ.
ಇದು ಆರೋಗ್ಯ, ಶಿಕ್ಷಣ, ಮತ್ತು ಕೃಷಿ ಕ್ಷೇತ್ರಗಳಲ್ಲಿ ಕ್ರಾಂತಿಕಾರಿ ಬದಲಾವಣೆಗಳನ್ನು ತರುತ್ತಿದೆ.
ಭಾರತದಲ್ಲಿ ಅನೇಕ ಕಂಪನಿಗಳು AI ಬಳಸಿ ಹೊಸ ಉತ್ಪನ್ನಗಳನ್ನು ರಚಿಸುತ್ತಿವೆ.
"""


def main():
    os.makedirs("output", exist_ok=True)

    print("=" * 60)
    print("BILINGUAL TTS TEST — English + Kannada")
    print("=" * 60)

    # --- English ---
    print(f"\n🇬🇧 ENGLISH TTS")
    print(f"   Input: {len(EN_TEXT)} chars, {len(EN_TEXT.split())} words")

    print("   [1/2] Female voice...")
    result = text_to_speech(EN_TEXT, "output/test_en_female.mp3", language="en", voice="female")
    print(f"   ✅ {result['output_path']} | {result['processing_time_seconds']}s | {result['file_size_bytes']/1024:.1f} KB")

    print("   [2/2] Male voice...")
    result = text_to_speech(EN_TEXT, "output/test_en_male.mp3", language="en", voice="male")
    print(f"   ✅ {result['output_path']} | {result['processing_time_seconds']}s | {result['file_size_bytes']/1024:.1f} KB")

    # --- Kannada ---
    print(f"\n🇮🇳 KANNADA TTS (ಕನ್ನಡ)")
    print(f"   Input: {len(KN_TEXT)} chars")

    print("   [1/1] VITS model...")
    result = text_to_speech(KN_TEXT, "output/test_kn.wav", language="kn")
    print(f"   ✅ {result['output_path']} | {result['processing_time_seconds']}s | {result['file_size_bytes']/1024:.1f} KB")

    print("\n" + "=" * 60)
    print("[DONE] Check output/ folder for MP3 (English) and WAV (Kannada)")
    print("=" * 60)


if __name__ == "__main__":
    main()
