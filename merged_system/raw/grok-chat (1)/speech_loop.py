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

    async def handle_chunk(self, chunk: np.ndarray) -> None:
        tmpdir = tempfile.mkdtemp()
        tmp_path = Path(tmpdir) / "attempt.wav"
        sf.write(tmp_path, chunk, self.config.audio.sample_rate)

        raw, corrected = await self.processor.process(chunk, tmp_path, self.config.audio.sample_rate)

        normalized_attempt = raw.strip().lower()

        # ... (phrase matching and scoring logic from your snippets)

        if needs_correction and self.config.behavior.correction_echo_enabled:
            self.inner_voice.speak_corrected(
                corrected_text=corrected,
                raw_text=raw,
                prosody_source_wav=chunk,
                prosody_source_sr=self.config.audio.sample_rate,
            )

        if best and not needs_correction and audio_score >= 0.9:
            self.voice_profile.maybe_adapt_from_attempt(
                attempt_wav=chunk,
                style="neutral",
                quality_score=audio_score,
            )

        event = self.monitor.register(
            normalized_text=normalized_attempt,
            needs_correction=needs_correction,
            rms=rms,
        )

        if event:
            suggestions = self.advisor.suggest(event)
            for s in suggestions:
                print(f"[{event}] {s.title}: {s.description}")

    async def run(self) -> None:
        print("Starting the real-time voice mimicry loop...")
        # Your audio stream loop here, calling handle_chunk on chunks
        while True:
            # Placeholder for audio input loop
            await asyncio.sleep(1)  # Replace with real stream

if __name__ == "__main__":
    loop = SpeechLoop()
    asyncio.run(loop.run())
