# 🚀 Free Public Hosting Guide for VoiceCraft AI

This guide walks you through the best 100% free ways to host **VoiceCraft AI** publicly so anyone can access it online without paying anything.

---

## 🌟 Option 1: Hugging Face Spaces (RECOMMENDED for AI/ML Apps)

Because VoiceCraft AI uses PyTorch, OpenAI Whisper, and Hugging Face MMS TTS models, **Hugging Face Spaces** is the **best free platform**. It provides **16 GB RAM and 2 vCPUs for FREE forever**.

### Steps to Deploy:
1. **Sign Up**: Create a free account on [Hugging Face](https://huggingface.co/join).
2. **Create Space**:
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **"Create new Space"**.
   - **Space Name**: `voicecraft-ai` (or any name you prefer).
   - **License**: MIT (or Open Source).
   - **Select SDK**: Select **Docker** -> **Blank**.
   - **Space Hardware**: Choose **CPU basic • 2 vCPU • 16GB RAM** (Free).
   - Click **"Create Space"**.
3. **Upload Code**:
   - Option A: Clone the HF repository locally and push your project files (`git push`).
   - Option B: Use the **"Files"** tab on your Hugging Face Space page and upload all project files (including the `Dockerfile` provided).
4. **Done!** Hugging Face will automatically build and start your application. Your public link will look like:
   `https://<your-username>-voicecraft-ai.hf.space`

---

## ⚡ Option 2: Instant Public Access from your PC (Cloudflare / LocalTunnel)

If you want to share the app running on your machine **immediately** without uploading model files:

### Using LocalTunnel (Zero installation required):
1. Make sure your app is running locally:
   ```bash
   python app.py
   ```
2. In a new command prompt / terminal, run:
   ```bash
   npx localtunnel --port 8000
   ```
3. Copy the generated URL (e.g. `https://cool-app-123.loca.lt`) and share it with anyone!

---

## 🌐 Option 3: Render.com (Free Cloud Web Service)

1. Push your code to a **GitHub repository**.
2. Go to [Render.com](https://render.com) and create a free account.
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Environment: Select **Docker** (it will auto-detect the `Dockerfile`).
6. Click **Deploy Web Service**.

---

## 📋 Included Files for Deployment:
- `Dockerfile`: Pre-configured Python 3.10 environment with FFmpeg, PyTorch CPU, and Uvicorn.
- `.dockerignore`: Prevents temporary files from inflating build sizes.
- `Procfile`: Configured for PaaS platforms.
