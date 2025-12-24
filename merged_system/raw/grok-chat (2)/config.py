from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

@dataclass(slots=True)
class Paths:
    base_dir: Path = Path.home() / "jacksons_companion"
    voices_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    attempts_csv: Path = field(init=False)
    guidance_csv: Path = field(init=False)

    def __post_init__(self) -> None:
        self.voices_dir = self.base_dir / "voices"
        self.logs_dir = self.base_dir / "logs"
        self.attempts_csv = self.logs_dir / "attempts.csv"
        self.guidance_csv = self.logs_dir / "guidance_events.csv"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

@dataclass(slots=True)
class AudioSettings:
    sample_rate: int = 16000
    chunk_seconds: float = 2.5
    silence_rms_threshold: float = 0.02

@dataclass(slots=True)
class SpeechModelSettings:
    whisper_model: str = "base.en"
    tts_model: str = "tts_models/en/vctk/vits"

@dataclass(slots=True)
class CompanionConfig:
    paths: Paths = field(default_factory=Paths)
    audio: AudioSettings = field(default_factory=AudioSettings)
    speech: SpeechModelSettings = field(default_factory=SpeechModelSettings)

CONFIG = CompanionConfig()
