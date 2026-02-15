
// DOM Elements
const recordBtn = document.getElementById('record-btn');
const btnText = document.getElementById('btn-text');
const statusText = document.getElementById('status-text');
const chatBox = document.getElementById('chat-box');

// Audio Context & Recorder State
let audioContext;
let recorder;
let input;
let isRecording = false;

// Initialize
recordBtn.addEventListener('click', toggleRecording);

async function toggleRecording() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    try {
        // Init AudioContext on user gesture
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioContext.state === 'suspended') {
            await audioContext.resume();
        }

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        input = audioContext.createMediaStreamSource(stream);

        // Initialize Recorder
        recorder = new WavRecorder(input);
        recorder.record();

        isRecording = true;
        updateUI(true);
        console.log("Recording started...");

    } catch (err) {
        console.error("Error accessing microphone:", err);
        statusText.textContent = "Error: " + err.message;
        alert("Could not access microphone: " + err.message);
    }
}

function stopRecording() {
    console.log("Stopping recording...");
    recorder.stop();
    input.disconnect();

    // Stop tracks
    input.mediaStream.getTracks().forEach(track => track.stop());

    isRecording = false;
    updateUI(false);

    // Export WAV
    recorder.exportWAV((blob) => {
        sendAudioToServer(blob);
    });
}

function updateUI(recording) {
    if (recording) {
        recordBtn.classList.add('recording');
        btnText.textContent = "Stop Recording";
        statusText.textContent = "Listening...";
    } else {
        recordBtn.classList.remove('recording');
        btnText.textContent = "Tap to Speak";
        statusText.textContent = "Processing...";
    }
}

function sendAudioToServer(blob) {
    console.log(`Audio recorded: ${blob.size} bytes`);

    if (blob.size < 1000) {
        console.warn("Audio too short, ignoring.");
        statusText.textContent = "Too short. Try again.";
        return;
    }

    const formData = new FormData();
    formData.append('audio_data', blob, 'recording.wav');

    // UI Placeholder
    addMessage("...", "user-message");

    fetch('/process_audio', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            // Remove placeholder
            removePlaceholder();

            if (data.error) {
                addMessage("Error: " + data.error, "bot-message");
                statusText.textContent = "Error occurred.";
            } else {
                console.log("Response received:", data);
                addMessage(data.user_text, "user-message", data.detected_lang);
                addMessage(data.bot_reply, "bot-message", data.detected_lang);

                if (data.audio_url) {
                    // Determine absolute URL to avoid issues
                    const audioUrl = window.location.origin + data.audio_url;
                    playAudio(audioUrl);
                }
                statusText.textContent = "Ready";
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            removePlaceholder();
            addMessage("Server connection failed.", "bot-message");
            statusText.textContent = "Server Error";
        });
}

function removePlaceholder() {
    const messages = chatBox.getElementsByClassName('message');
    if (messages.length > 0) {
        const last = messages[messages.length - 1];
        if (last.textContent === "...") {
            last.remove();
        }
    }
}

function addMessage(text, className, lang = null) {
    const div = document.createElement('div');
    div.classList.add('message', className);

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');
    contentDiv.textContent = text;

    if (lang) {
        const langInfo = document.createElement('div');
        langInfo.classList.add('detection-info');
        langInfo.innerText = `Detected: ${lang}`;
        contentDiv.appendChild(langInfo);
    }

    div.appendChild(contentDiv);

    // Optional timestamp
    const timeDiv = document.createElement('div');
    timeDiv.classList.add('timestamp');
    const now = new Date();
    timeDiv.textContent = now.getHours() + ":" + String(now.getMinutes()).padStart(2, '0');
    div.appendChild(timeDiv);

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function playAudio(url) {
    console.log("Playing audio:", url);
    const audio = new Audio(url);
    audio.play().catch(e => console.error("Audio play error:", e));
}


// --- Robust WAV Recorder Implementation ---
// Based on Recorder.js
class WavRecorder {
    constructor(source, cfg) {
        this.config = cfg || {};
        this.bufferLen = 4096;
        this.context = source.context;
        this.node = (this.context.createScriptProcessor ||
            this.context.createJavaScriptNode).call(this.context,
                this.bufferLen, 1, 1); // MONO recording

        this.recording = false;
        this.recBuffers = [];
        this.recLength = 0;

        this.node.onaudioprocess = (e) => {
            if (!this.recording) return;
            const buffer = e.inputBuffer.getChannelData(0);
            this.recBuffers.push(new Float32Array(buffer));
            this.recLength += buffer.length;
        };

        source.connect(this.node);
        this.node.connect(this.context.destination);
    }

    record() {
        this.recBuffers = [];
        this.recLength = 0;
        this.recording = true;
    }

    stop() {
        this.recording = false;
    }

    exportWAV(cb) {
        const buffer = this.mergeBuffers(this.recBuffers, this.recLength);
        const dataview = this.encodeWAV(buffer);
        const audioBlob = new Blob([dataview], { type: 'audio/wav' });
        cb(audioBlob);
    }

    mergeBuffers(recBuffers, recLength) {
        const result = new Float32Array(recLength);
        let offset = 0;
        for (let i = 0; i < recBuffers.length; i++) {
            result.set(recBuffers[i], offset);
            offset += recBuffers[i].length;
        }
        return result;
    }

    encodeWAV(samples) {
        const buffer = new ArrayBuffer(44 + samples.length * 2);
        const view = new DataView(buffer);
        const sampleRate = this.context.sampleRate;

        // RIFF chunk descriptor
        this.writeString(view, 0, 'RIFF');
        view.setUint32(4, 36 + samples.length * 2, true);
        this.writeString(view, 8, 'WAVE');

        // fmt sub-chunk
        this.writeString(view, 12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true); // PCM format
        view.setUint16(22, 1, true); // Mono
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * 2, true);
        view.setUint16(32, 2, true);
        view.setUint16(34, 16, true);

        // data sub-chunk
        this.writeString(view, 36, 'data');
        view.setUint32(40, samples.length * 2, true);

        // Write PCM samples
        this.floatTo16BitPCM(view, 44, samples);

        return view;
    }

    floatTo16BitPCM(output, offset, input) {
        for (let i = 0; i < input.length; i++, offset += 2) {
            const s = Math.max(-1, Math.min(1, input[i]));
            output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }
    }

    writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    }
}
