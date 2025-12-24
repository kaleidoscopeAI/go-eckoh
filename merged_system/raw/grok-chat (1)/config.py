from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

@dataclass(slots=True)
class Paths:
    base_dir: Path = Path.home() / "autism_companion"
    voices_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    metrics_csv: Path = field(init=False)
    guidance_csv: Path = field(init=False)

    def __post_init__(self) -> None:
        self.voices_dir = self.base_dir / "voices"
        self.logs_dir = self.base_dir / "logs"
        self.metrics_csv = self.base_dir / "metrics.csv"
        self.guidance_csv = self.base_dir / "guidance_events.csv"
        self.ensure()

    def ensure(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

@dataclass(slots=True)
class AudioSettings:
    sample_rate: int = 16000
    channels: int = 1
    chunk_seconds: float = 2.0
    silence_rms_threshold: float = 0.02

@dataclass(slots=True)
class SpeechModelSettings:
    whisper_model: str = "small.en"
    tts_model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"

@dataclass(slots=True)
class BehaviorSettings:
    correction_echo_enabled: bool = True
    support_voice_enabled: bool = False

@dataclass(slots=True)
class CompanionConfig:
    child_name: str = "Jackson"
    paths: Paths = field(default_factory=Paths)
    audio: AudioSettings = field(default_factory=AudioSettings)
    speech: SpeechModelSettings = field(default_factory=SpeechModelSettings)
    behavior: BehaviorSettings = field(default_factory=BehaviorSettings)

CONFIG = CompanionConfig()
