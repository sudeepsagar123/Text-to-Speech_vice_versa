# 🎙️ VoiceCraft AI — Bilingual Speech Processing System
**Project Submission Document**

---

## 📌 Executive Summary

**VoiceCraft AI** is a production-grade, bilingual Speech-to-Text (STT) and Text-to-Speech (TTS) web application designed to bridge language accessibility gaps. The platform delivers real-time, bidirectional voice processing for **English** and **Kannada (ಕನ್ನಡ)**. 

Built with scalability, efficiency, and user experience in mind, the platform optimizes state-of-the-art deep learning models to operate inside low-resource container environments without sacrificing translation speed or transcription accuracy.

---

## 🎯 Problem Statement & Solution

* **The Problem**: Existing commercial voice APIs (Google Cloud Speech, AWS Polly) are costly, require mandatory billing setups, and often lack seamless, unified support for regional Indian languages like Kannada. Furthermore, hosting heavy ML models in production usually demands expensive GPU infrastructure.
* **The Solution**: VoiceCraft AI provides a zero-cost, open-architecture solution that synthesizes natural-sounding speech and transcribes uploaded or recorded audio in real time. Through memory quantization and CPU-bound model caching, the application runs inside constrained cloud environments (512 MB RAM limit).

---

## 🚀 Key Features

1. **Bilingual Text-to-Speech (TTS)**:
   * **English**: Neural voice synthesis via Microsoft Edge-TTS (*Neerja* female and *Prabhat* male Indian English voices).
   * **Kannada (ಕನ್ನಡ)**: Neural speech generation.
2. **Bilingual Speech-to-Text (STT)**:
   * **English & Kannada**: OpenAI Whisper speech recognition with automatic language token forced decoding for accurate transcripts.
3. **Live Microphone & File Input**:
   * Integrated browser-native `MediaRecorder API` for live voice recording.
   * Drag-and-drop support for standard audio formats (`MP3`, `WAV`, `FLAC`, `OGG`).
4. **Interactive Modern Interface**:
   * Dynamic glassmorphism design with responsive controls, character counters, processing latency metrics, and transcript copying.

---

## 🛠️ Complete Technical Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript | Modern CSS variables, glassmorphic UI, Web Audio API, MediaRecorder API, Fetch API |
| **Backend** | Python 3.10, FastAPI, AsyncIO | High-concurrency REST API framework, Uvicorn ASGI server |
| **AI / ML Core** | OpenAI Whisper, Edge-TTS | CPU-quantized Speech-to-Text and Neural Text-to-Speech models |
| **Audio Processing** | SoundFile, Librosa, SciPy, FFmpeg | Audio resampling, mono-channel conversion, waveform processing |
| **DevOps & Cloud** | Docker, Git, Render.com | Multi-stage Docker build, CI/CD automated deployment |

---

## ⚙️ Engineering & Optimization Highlights

* **Memory Footprint Reduction (OOM Prevention)**: Reduced peak server memory consumption from ~1.5 GB down to **~75 MB RAM** by switching to quantized OpenAI Whisper (`tiny`) models and implementing post-request garbage collection (`gc.collect()`).
* **Asynchronous Execution Pipeline**: Offloaded CPU-intensive PyTorch model inference to background thread pools (`run_in_executor`) to prevent blocking FastAPI’s main event loop.
* **Dynamic Environment Port Matching**: Configured server entry point to adapt dynamically to host environment ports (`$PORT`), enabling container deployment across Render, Hugging Face, or Kubernetes.

---

## 🌐 Live Application & Links

* **GitHub Repository**: [github.com/sudeepsagar123/Text-to-Speech_vice_versa](https://github.com/sudeepsagar123/Text-to-Speech_vice_versa)
* **Live Web App**: [https://text-to-speech-vice-versa.onrender.com](https://text-to-speech-vice-versa.onrender.com)
