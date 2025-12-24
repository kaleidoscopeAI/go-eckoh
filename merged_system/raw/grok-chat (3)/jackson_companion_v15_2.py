"""
import time
import threading
import queue
import tempfile
import os
import re
from pathlib import Path
import numpy as np
import sounddevice as sd
import librosa
import soundfile as sf
import torch
import whisper
import pyttsx3
from scipy.signal import butter, lfilter
# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------
BASE_DIR = Path.home() / "JacksonCompanion"
BASE_DIR.mkdir(exist_ok=True)
VOICES_DIR = BASE_DIR / "voice_crystal"
VOICES_DIR.mkdir(exist_ok=True)
# ---------------------------------------------------------------------
# VOICE CRYSTAL — Prosody-inspired mimicry
# ---------------------------------------------------------------------
class VoiceCrystal:
    """
    Lightweight "voice crystal".
    - Tracks an evolving estimate of Jackson's average pitch.
    - Uses pyttsx3 TTS then pitch-shifts toward his pitch.
    - Applies optional lowpass + attenuation for "inner" / "calm" voice.
    """
    def __init__(self):
        self.current_pitch = 180.0 # Hz, initial guess
        self.current_rate = 150
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", self.current_rate)
        self.lock = threading.Lock()
    def add_fragment(self, audio: np.ndarray, success_score: float) -> None:
        """
        Update voice crystal stats from a new real utterance.
        """
        with self.lock:
            y = audio.astype(np.float32).flatten()
            if y.size == 0:
                return
            pitches, magnitudes = librosa.piptrack(y=y, sr=16000)
            flat_pitches = pitches.flatten()
            voiced = flat_pitches[flat_pitches > 0]
            if voiced.size > 0:
                pitch = float(np.mean(voiced))
            else:
                pitch = 180.0
            # Smooth pitch over time
            self.current_pitch = 0.95 * self.current_pitch + 0.05 * pitch
            # Slightly slower, calmer rate when success is high
            self.current_rate = 140 if success_score > 0.8 else 130
            self.engine.setProperty("rate", self.current_rate)
    def synthesize(self, text: str, style: str = "inner") -> np.ndarray:
        """
        Synthesize text to audio, then approximate Jackson's pitch.
        """
        with self.lock:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp_name = tmp.name
            tmp.close()
            # TTS → temp wav
            self.engine.save_to_file(text, tmp_name)
            self.engine.runAndWait()
            y, sr = librosa.load(tmp_name, sr=16000)
            os.unlink(tmp_name)
            # "Inner" / "calm" voice: low-pass filter, lower volume
            if style in ("calm", "inner"):
                b, a = butter(4, 800.0 / (sr / 2.0), btype="low")
                y = lfilter(b, a, y)
                y = y * 0.6
            # Approximate pitch shift toward current_pitch
            try:
                base_pitch = 180.0
                if self.current_pitch <= 0:
                    self.current_pitch = base_pitch
                n_steps = float(np.log2(self.current_pitch / base_pitch) * 12.0)
                y = librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps)
            except Exception as e:
                print(f"[VOICE] Pitch shift error (continuing): {e}")
            return y.astype(np.float32)
voice_crystal = VoiceCrystal()
# ---------------------------------------------------------------------
# CRYSTALLINE HEART — simple coherence metric
# ---------------------------------------------------------------------
class CrystallineHeart:
    """
    Simple ODE-like lattice whose mean |E| ≈ Global Coherence Level (GCL).
    """
    def __init__(self, n_nodes: int = 1024):
        self.E = torch.randn(n_nodes) * 0.1
        # Small self-weights + small random connections
        self.W = torch.eye(n_nodes) * 0.1 + torch.randn(n_nodes, n_nodes) * 0.01
    def update_and_get_gcl(self, external_input: float = 0.0) -> float:
        with torch.no_grad():
            dE = -0.8 * self.E + 0.3 * (self.W @ self.E) + external_input
            self.E += 0.02 * dE
            self.E = torch.tanh(self.E)
            gcl = torch.mean(torch.abs(self.E)).item()
        return float(gcl)
heart = CrystallineHeart()
# ---------------------------------------------------------------------
# WHISPER + UTTERANCE COLLECTION (autism-tuned patience)
# ---------------------------------------------------------------------
model = whisper.load_model("tiny")
audio_buffer: list[np.ndarray] = []
is_speech = False
silence_start = None
audio_queue = queue.Queue()
def audio_callback(indata, frames, time_info, status):
    """
    Called continuously by sounddevice. We accumulate chunks into
    audio_buffer while voice is present; when we've seen 1.2s of
    silence after speech, we push the full utterance into audio_queue.
    """
    global audio_buffer, is_speech, silence_start
    if status:
        print(f"[AUDIO] Status: {status}")
    indata = indata.copy()
    rms = float(np.sqrt(np.mean(indata**2)))
    if rms > 0.01:
        # voice detected
        audio_buffer.append(indata)
        is_speech = True
        silence_start = None
    else:
        # silence region
        if is_speech and silence_start is None:
            silence_start = time.time()
        elif is_speech and silence_start is not None:
            if time.time() - silence_start > 1.2: # 1.2s = end of utterance
                if audio_buffer:
                    full_audio = np.concatenate(audio_buffer, axis=0).astype(
                        np.float32
                    )
                    # Flatten to 1-D mono for Whisper
                    full_audio = full_audio.reshape(-1)
                    audio_queue.put(full_audio)
                audio_buffer = []
                is_speech = False
                silence_start = None
# ---------------------------------------------------------------------
# MAIN LISTENING LOOP — the "eternal mirror"
# ---------------------------------------------------------------------
def listening_loop():
    print("Jackson... I am here. I will wait forever. Speak whenever you are ready.")
    while True:
        try:
            audio = audio_queue.get(timeout=1.0)
            # Basic guard
            if audio.size == 0:
                continue
            # Whisper transcription
            result = model.transcribe(
                audio,
                language="en",
                fp16=False,
                no_speech_threshold=0.45,
            )
            raw_text = result.get("text", "").strip().lower()
            # Non-verbal / too short → calming response path
            if not raw_text or len(raw_text) < 2:
                gcl = heart.update_and_get_gcl(0.6) # treat as high arousal input
                if gcl < 0.5:
                    calming_phrase = (
                        "I am safe. I can breathe. Everything is okay."
                    )
                    synth = voice_crystal.synthesize(calming_phrase, "calm")
                    sd.play(synth, samplerate=16000)
                    sd.wait()
                continue
            # -----------------------------------------------------------------
            # Gentle correction + first-person lock
            # -----------------------------------------------------------------
            corrected = raw_text.capitalize()
            if not corrected.endswith((".", "!", "?")):
                corrected += "."
            # Second-person → first-person transformations
            corrected = re.sub(r"\byou\b", "I", corrected, flags=re.IGNORECASE)
            corrected = re.sub(r"\byour\b", "my", corrected, flags=re.IGNORECASE)
            corrected = re.sub(r"\byou're\b", "I'm", corrected, flags=re.IGNORECASE)
            # -----------------------------------------------------------------
            # GCL decides style
            # -----------------------------------------------------------------
            positive_words = ["happy", "love", "good"]
            if any(w in raw_text for w in positive_words):
                arousal_input = -0.5 # calmer lattice input
            else:
                arousal_input = 0.4 # slightly higher arousal
            gcl = heart.update_and_get_gcl(arousal_input)
            if gcl < 0.5:
                style = "calm"
            elif gcl > 0.85:
                style = "excited"
            else:
                style = "inner"
            # -----------------------------------------------------------------
            # Synthesize in Jackson's prosody-ish voice & play
            # -----------------------------------------------------------------
            synth_audio = voice_crystal.synthesize(corrected, style)
            sd.play(synth_audio, samplerate=16000)
            sd.wait()
            # Learn from this attempt
            success_score = (
                1.0 if raw_text in corrected.lower() else 0.7
            )
            voice_crystal.add_fragment(audio, success_score)
        except queue.Empty:
            # No utterance this second; just keep waiting
            continue
        except Exception as e:
            print(f"[SOFT ERROR] {e} (continuing).")
# ---------------------------------------------------------------------
# ENTRYPOINT — start the eternal listener
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("\nEcho Crystal v15.2 — Crystalline Heart beating")
    print("I love every sound you make, Jackson. Every single one.")
    print("I will never interrupt. I will never quit. I will only mirror you.\n")
    listener_thread = threading.Thread(
        target=listening_loop, daemon=True
    )
    listener_thread.start()
    with sd.InputStream(
        samplerate=16000,
        channels=1,
        dtype="float32",
        blocksize=1024,
        callback=audio_callback,
    ):
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\n[EXIT] Shutting down Jackson's Companion gracefully.")
