# Use official lightweight Python image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Install system audio dependencies (FFmpeg and libsndfile for Whisper & audio processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Upgrade pip, setuptools, and wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install CPU PyTorch first (faster download & smaller image size) followed by other requirements
RUN pip install --no-cache-dir torch torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create output folder and set permissions
RUN mkdir -p output && chmod 777 output

# Expose port (7860 is default for Hugging Face Spaces; Render handles PORT dynamically)
EXPOSE 7860

# Run FastAPI app
CMD ["python", "app.py"]
