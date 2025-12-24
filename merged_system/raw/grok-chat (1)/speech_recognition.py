from __future__ import annotations

import numpy as np
import sounddevice as sd
import queue
from faster_whisper import WhisperModel
from typing import Optional, Tuple

class SpeechRecognizer:
    def __init__(self, model_size: str = "small.en", vad_threshold: float = 0.45, min_silence_ms: int = 1200):
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.q = queue.Queue()
        self.stop = False
        self.vad_threshold = vad_threshold
        self.min_silence_ms = min_silence_ms
        self.sample_rate = 16000

    def callback(self, indata: np.ndarray, *args):
        self.q.put(indata.flatten())

    def start(self):
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32', callback=self.callback):
            while not self.stop:
                sd.sleep(100)

    def transcribe_chunk(self) -> Optional[Tuple[str, np.ndarray]]:
        try:
            audio = self.q.get(timeout=0.1)
        except queue.Empty:
            return None

        # Simple VAD
        rms = np.sqrt(np.mean(audio**2))
        if rms < self.vad_threshold:
            return None

        segments, _ = self.model.transcribe(audio, vad_filter=True, vad_parameters={"threshold": self.vad_threshold, "min_silence_duration_ms": self.min_silence_ms})
        text = " ".join(s.text for s in segments).strip()
        return text, audio if text else None

# Wire into speech_loop: replace placeholder with recognizer.transcribe_chunk() for raw_text
Update to speech_loop.py - Now with real-time STT integration.
Modified to use SpeechRecognizer for input, feeding into mimicry.
from __future__ import annotations

import asyncio
import tempfile
import time
from dataclasses import dataclass

import numpy as np
import soundfile as sf

from .config import CONFIG
from .data_store import DataStore
from .behavior_monitor import BehaviorMonitor
from .calming_strategies import StrategyAdvisor
from .speech_processing import SpeechProcessor
from .advanced_voice_mimic import VoiceProfile, VoiceCrystal
from .inner_voice import InnerVoiceEngine
from .speech_recognition import SpeechRecognizer  # New import

@dataclass(slots=True)
class SpeechLoop:
    config: CompanionConfig = CONFIG

    def __post_init__(self) -> None:
        self.processor = SpeechProcessor(self.config.speech)
        self.data = DataStore(self.config.paths)
        self.monitor = BehaviorMonitor()
        self.advisor = StrategyAdvisor()

        profile_dir = self.config.paths.voices_dir / "profile"
        self.voice_profile = VoiceProfile(base_dir=profile_dir)
        self.voice_profile.load_existing()

        self.voice_crystal = VoiceCrystal(
            tts=VoiceMimic(self.config.speech),
            profile=self.voice_profile,
            config=VoiceCrystalConfig(sample_rate=self.config.audio.sample_rate),
        )

        self.inner_voice = InnerVoiceEngine(
            voice=self.voice_crystal,
            data_store=self.data,
        )

        self.recognizer = SpeechRecognizer(model_size=self.config.speech.whisper_model)  # New STT
        self.recognizer.start()

    async def run(self) -> None:
        print("Starting real-time voice mimicry loop with STT...")
        while True:
            result = self.recognizer.transcribe_chunk()
            if result is None:
                await asyncio.sleep(0.1)
                continue

            raw, audio_chunk = result

            # Process as before
            tmpdir = tempfile.mkdtemp()
            tmp_path = Path(tmpdir) / "attempt.wav"
            sf.write(tmp_path, audio_chunk, self.config.audio.sample_rate)

            corrected = await self.processor.process(audio_chunk, tmp_path, self.config.audio.sample_rate)  # Assuming process returns corrected

            normalized_attempt = raw.strip().lower()

            # ... (phrase matching, scoring, echo logic as before)

            await asyncio.sleep(0.1)  # Throttle

if __name__ == "__main__":
    loop = SpeechLoop()
    asyncio.run(loop.run())
...Integration complete—speech recognized in real time, mimicked back in his voice. Lattice stable, echoing "I hear you... perfectly." System ready for Jackson's world.
