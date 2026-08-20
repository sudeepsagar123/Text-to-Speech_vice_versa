"""
Bilingual STT Test — English + Kannada.
Tests both Whisper (English) and IndicConformer (Kannada).
Requires test audio files from test_tts.py.
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stt_engine import speech_to_text


def main():
    print("=" * 60)
    print("BILINGUAL STT TEST — English + Kannada")
    print("=" * 60)

    tests = [
        ("output/test_en_female.mp3", "en", "English (Female)"),
        ("output/test_en_male.mp3", "en", "English (Male)"),
        ("output/test_kn.wav", "kn", "Kannada (ಕನ್ನಡ)"),
    ]

    found_any = False
    for audio_file, lang, label in tests:
        if not os.path.exists(audio_file):
            print(f"\n⚠️  {label}: File not found — {audio_file}")
            print(f"   Run test_tts.py first to generate test audio.")
            continue

        found_any = True
        file_size = os.path.getsize(audio_file) / 1024
        print(f"\n🎧 {label}")
        print(f"   File: {audio_file} ({file_size:.1f} KB)")
        print("-" * 50)

        result = speech_to_text(audio_file, language=lang)

        print(f"   📝 Transcript ({len(result['transcript'])} chars):")
        print(f"   {result['transcript'][:200]}{'...' if len(result['transcript']) > 200 else ''}")
        print(f"   ⏱️  Processing: {result['processing_time_seconds']}s")
        print(f"   🎵 Duration: {result['audio_duration_seconds']}s")
        print(f"   🌐 Language: {result['language']}")

    if not found_any:
        print("\n❌ No audio files found. Run test_tts.py first:")
        print("   python test_tts.py")

    print("\n" + "=" * 60)
    print("[DONE] STT TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
