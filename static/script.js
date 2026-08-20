// ===== VoiceCraft AI — Bilingual Frontend Logic =====

// === Language state ===
let ttsLang = 'en';
let sttLang = 'en';

// === TTS Language Toggle ===
function setTTSLang(lang) {
    ttsLang = lang;
    const toggle = document.getElementById('tts-lang-toggle');
    toggle.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // Show/hide voice selector (English only)
    const voiceGroup = document.getElementById('tts-voice-group');
    voiceGroup.style.display = lang === 'en' ? 'block' : 'none';

    // Update placeholder text
    const textarea = document.getElementById('tts-text');
    if (lang === 'kn') {
        textarea.placeholder = 'ಇಲ್ಲಿ ಕನ್ನಡ ಪಠ್ಯವನ್ನು ಟೈಪ್ ಮಾಡಿ... ದೊಡ್ಡ ಪ್ಯಾರಾಗ್ರಾಫ್‌ಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ.';
    } else {
        textarea.placeholder = 'Paste your text here... supports long paragraphs, articles, and more.';
    }
}

// === STT Language Toggle ===
function setSTTLang(lang) {
    sttLang = lang;
    const toggle = document.getElementById('stt-lang-toggle');
    toggle.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });
}

// === TTS: Character counter ===
const ttsText = document.getElementById('tts-text');
const charCount = document.getElementById('tts-char-count');

ttsText.addEventListener('input', () => {
    const len = ttsText.value.length;
    charCount.textContent = `${len.toLocaleString()} characters`;
});

// === TTS: Convert text to speech ===
async function handleTTS() {
    const text = ttsText.value.trim();
    if (!text) {
        showStatus('tts-status', 'Please enter some text first.', 'error');
        return;
    }

    const voice = document.getElementById('tts-voice').value;
    const btn = document.getElementById('tts-btn');
    const player = document.getElementById('tts-player');
    const audio = document.getElementById('tts-audio');
    const meta = document.getElementById('tts-meta');

    btn.classList.add('loading');
    btn.disabled = true;
    player.classList.remove('visible');

    const langLabel = ttsLang === 'kn' ? 'Kannada' : 'English';
    showStatus('tts-status', `🔄 Converting ${langLabel} text to speech... This may take a moment.`, 'info');

    try {
        const formData = new FormData();
        formData.append('text', text);
        formData.append('language', ttsLang);
        formData.append('voice', voice);

        const response = await fetch('/api/tts', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'TTS conversion failed');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        audio.src = url;
        player.classList.add('visible');

        const processingTime = response.headers.get('X-Processing-Time') || '?';
        const textLength = response.headers.get('X-Text-Length') || text.length;
        const voiceUsed = response.headers.get('X-Voice-Used') || voice;

        meta.innerHTML = `
            <span>⏱️ ${processingTime}s</span>
            <span>📝 ${parseInt(textLength).toLocaleString()} chars</span>
            <span>🎙️ ${voiceUsed}</span>
            <span>📦 ${(blob.size / 1024).toFixed(1)} KB</span>
        `;

        showStatus('tts-status', `✅ ${langLabel} speech generated successfully!`, 'success');
    } catch (err) {
        showStatus('tts-status', `❌ ${err.message}`, 'error');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

// === STT: File upload handling ===
let selectedFile = null;

function handleFileSelect(input) {
    if (input.files && input.files[0]) {
        selectedFile = input.files[0];
        showFileInfo(selectedFile);
    }
}

function showFileInfo(file) {
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    fileName.textContent = `${file.name} (${sizeMB} MB)`;
    fileInfo.classList.add('visible');
}

function removeFile() {
    selectedFile = null;
    document.getElementById('stt-file').value = '';
    document.getElementById('file-info').classList.remove('visible');
}

// === STT: Drag and drop ===
const uploadZone = document.getElementById('upload-zone');

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        selectedFile = e.dataTransfer.files[0];
        document.getElementById('stt-file').files = e.dataTransfer.files;
        showFileInfo(selectedFile);
    }
});

// === STT: Microphone Recording ===
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

async function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) audioChunks.push(e.data);
        };

        mediaRecorder.onstop = () => {
            const blob = new Blob(audioChunks, { type: 'audio/webm' });
            selectedFile = new File([blob], 'recording.webm', { type: 'audio/webm' });
            showFileInfo(selectedFile);
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        isRecording = true;

        const btn = document.getElementById('record-btn');
        btn.classList.add('recording');
        document.getElementById('record-icon').textContent = '⏹️';
        document.getElementById('record-text').textContent = 'Stop Recording';

        const langLabel = sttLang === 'kn' ? 'ಕನ್ನಡ' : 'English';
        showStatus('stt-status', `🎤 Recording (${langLabel})... Click stop when done.`, 'info');
    } catch (err) {
        showStatus('stt-status', `❌ Microphone access denied: ${err.message}`, 'error');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    isRecording = false;

    const btn = document.getElementById('record-btn');
    btn.classList.remove('recording');
    document.getElementById('record-icon').textContent = '🎤';
    document.getElementById('record-text').textContent = 'Start Recording';

    hideStatus('stt-status');
}

// === STT: Transcribe audio ===
async function handleSTT() {
    if (!selectedFile) {
        showStatus('stt-status', 'Please upload an audio file or record your voice first.', 'error');
        return;
    }

    const btn = document.getElementById('stt-btn');
    const output = document.getElementById('transcript-output');

    btn.classList.add('loading');
    btn.disabled = true;
    output.classList.remove('visible');

    const langLabel = sttLang === 'kn' ? 'Kannada' : 'English';
    showStatus('stt-status', `🔄 Transcribing ${langLabel}... This may take a while for long recordings.`, 'info');

    try {
        const formData = new FormData();
        formData.append('audio', selectedFile);
        formData.append('language', sttLang);

        const response = await fetch('/api/stt', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Transcription failed');
        }

        const result = await response.json();

        document.getElementById('transcript-text').textContent = result.transcript;
        document.getElementById('transcript-meta').innerHTML = `
            <span>⏱️ Processed in ${result.processing_time_seconds}s</span>
            <span>🎵 ${result.audio_duration_seconds}s audio</span>
            <span>📊 ${result.num_segments} segments</span>
            <span>🌐 ${result.language === 'kn' ? 'ಕನ್ನಡ' : 'English'}</span>
        `;
        output.classList.add('visible');

        showStatus('stt-status', '✅ Transcription complete!', 'success');
    } catch (err) {
        showStatus('stt-status', `❌ ${err.message}`, 'error');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

// === Copy transcript ===
function copyTranscript() {
    const text = document.getElementById('transcript-text').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const copyBtn = document.querySelector('.transcript-output__copy');
        copyBtn.textContent = '✅ Copied!';
        setTimeout(() => { copyBtn.textContent = '📋 Copy'; }, 2000);
    });
}

// === Status helpers ===
function showStatus(id, message, type) {
    const el = document.getElementById(id);
    el.className = `status visible status--${type}`;
    el.textContent = message;
}

function hideStatus(id) {
    const el = document.getElementById(id);
    el.className = 'status';
}
