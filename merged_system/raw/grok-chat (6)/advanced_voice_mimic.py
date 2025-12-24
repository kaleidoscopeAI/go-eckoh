from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Optional

import numpy as np
import time

from .config import AudioSettings
from .voice_mimic import VoiceMimic
from .prosody import extract_prosody, apply_prosody_to_tts

Style = Literal["neutral", "calm", "excited"]
Mode = Literal["outer", "inner", "coach"]

@dataclass(slots=True)
class VoiceSample:
    path: Path
    style: Style
    rms: float
    duration_s: float
    added_ts: float

@dataclass(slots=True)
class VoiceProfile:
    base_dir: Path
    samples: Dict[Style, List[VoiceSample]] = field(default_factory=lambda: {"neutral": [], "calm": [], "excited": []})
    max_samples_per_style: int = 32

    def _compute_rms(self, wav: np.ndarray) -> float:
        if wav.size == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(wav))))

    def add_sample_from_wav(self, wav: np.ndarray, style: Style, name: Optional[str] = None) -> Path:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        if name is None:
            name = time.strftime("%Y%m%d_%H%M%S")
        out_path = self.base_dir / f"{style}_{name}.wav"
        sf.write(out_path, wav, 16000)
        rms = self._compute_rms(wav)
        duration_s = float(len(wav) / 16000.0)
        sample = VoiceSample(
            path=out_path,
            style=style,
            rms=rms,
            duration_s=duration_s,
            added_ts=time.time(),
        )
        self.samples[style].append(sample)
        # Slow drift: prune oldest if too many
        if len(self.samples[style]) > self.max_samples_per_style:
            self.samples[style].sort(key=lambda s: s.added_ts)
            self.samples[style] = self.samples[style][-self.max_samples_per_style:]
        return out_path

    def load_existing(self) -> None:
        if not self.base_dir.exists():
            return
        for wav_path in self.base_dir.glob("*.wav"):
            stem = wav_path.stem
            if "_" not in stem:
                continue
            style_str, _ = stem.split("_", 1)
            if style_str not in ("neutral", "calm", "excited"):
                continue
            style: Style = style_str  # type: ignore
            wav, sr = sf.read(wav_path)
            rms = self._compute_rms(wav)
            duration_s = float(len(wav) / sr)
            sample = VoiceSample(
                path=wav_path,
                style=style,
                rms=rms,
                duration_s=duration_s,
                added_ts=wav_path.stat().st_mtime,
            )
            self.samples[style].append(sample)

    def pick_reference(self, style: Style, min_duration_s: float = 1.0) -> Optional[Path]:
        candidates = [s for s in self.samples.get(style, []) if s.duration_s >= min_duration_s]
        if not candidates:
            return None
        # Pick random for variety
        return random.choice(candidates).path

    def maybe_adapt_from_attempt(self, attempt_wav: np.ndarray, style: Style, quality_score: float = 1.0) -> None:
        if quality_score >= 0.9:  # only add very good attempts
            self.add_sample_from_wav(attempt_wav, style, name=None)

@dataclass(slots=True)
class VoiceCrystalConfig:
    sample_rate: int
    inner_volume_scale: float = 0.55
    coach_volume_scale: float = 1.2
    inner_lowpass_window_ms: float = 18.0
    coach_compression_ratio: float = 0.8
    prosody_strength_pitch: float = 1.0
    prosody_strength_energy: float = 1.0

@dataclass(slots=True)
class VoiceCrystal:
    tts: VoiceMimic
    profile: VoiceProfile
    config: VoiceCrystalConfig

    def _moving_average(self, wav: np.ndarray, window_ms: float) -> np.ndarray:
        window_size = int(self.config.sample_rate * (window_ms / 1000.0))\n        if window_size % 2 == 0:
            window_size += 1
        return np.convolve(wav, np.ones(window_size) / window_size, mode="same")

    def _apply_mode(self, wav: np.ndarray, mode: Mode) -> np.ndarray:
        if mode == "inner":
            smoothed = self._moving_average(wav, self.config.inner_lowpass_window_ms)
            rms = np.sqrt(np.mean(smoothed**2) + 1e-6)
            target_rms = rms * self.config.inner_volume_scale
            smoothed = np.tanh(smoothed / (rms + 1e-6)) * target_rms
            return smoothed
        if mode == "coach":
            return wav * self.config.coach_volume_scale
        return wav

    def speak(self, text: str, style: Style = "neutral", mode: Mode = "outer", prosody_source_wav: Optional[np.ndarray] = None, prosody_source_sr: Optional[int] = None) -> None:
        if not text:
            return

        ref = self.profile.pick_reference(style)
        if ref is not None:
            self.tts.update_voiceprint(ref)

        wav = self.tts.synthesize(text)
        if wav.size == 0:
            return

        if prosody_source_wav is not None:
            sr = prosody_source_sr or self.config.sample_rate
            pros = extract_prosody(prosody_source_wav, sr)
            wav = apply_prosody_to_tts(
                wav,
                self.config.sample_rate,
                pros,
                strength_pitch=self.config.prosody_strength_pitch,
                strength_energy=self.config.prosody_strength_energy,
            )

        processed = self._apply_mode(wav, mode)
        # Play or save as needed; assuming audio_io in loop handles play
        print(f"Speaking in {mode} mode: {text}")  # Placeholder for play
