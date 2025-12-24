from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional

import csv
import time
from pathlib import Path

EventType = Literal["meltdown_risk", "high_energy", "anxious", "calm", "success"]

@dataclass(slots=True)
class GuidanceEvent:
    timestamp: float
    event_type: EventType
    title: str
    message: str

@dataclass(slots=True)
class GuidanceLogger:
    path: Path
    events: List[GuidanceEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open("r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.events.append(
                    GuidanceEvent(
                        timestamp=float(row["timestamp"]),
                        event_type=row["event_type"],
                        title=row["title"],
                        message=row["message"],
                    )
                )

    def log(self, event_type: EventType, title: str, message: str) -> None:
        ts = time.time()
        event = GuidanceEvent(timestamp=ts, event_type=event_type, title=title, message=message)
        self.events.append(event)
        with self.path.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "event_type", "title", "message"])
            if self.path.stat().st_size == 0:
                writer.writeheader()
            writer.writerow({"timestamp": ts, "event_type": event_type, "title": title, "message": message})

@dataclass(slots=True)
class GuidanceEngine:
    logger: GuidanceLogger
    parent_phrases: Dict[EventType, List[str]] = field(default_factory=lambda: {
        "meltdown_risk": ["Everything is okay. Close my eyes and breathe."],
        "anxious": ["I am safe. Let's take a deep breath."],
        "success": ["Great job! I did it."]
    })

    def add_parent_phrase(self, event_type: EventType, phrase: str) -> None:
        if event_type not in self.parent_phrases:
            self.parent_phrases[event_type] = []
        self.parent_phrases[event_type].append(phrase)

    def get_guidance(self, event_type: EventType) -> Optional[str]:
        phrases = self.parent_phrases.get(event_type, [])
        if phrases:
            return np.random.choice(phrases)
        return None

    def trigger(self, event_type: EventType) -> None:
        message = self.get_guidance(event_type)
        if message:
            self.logger.log(event_type, "Guidance Triggered", message)
            # Integrate with voice: speak(message, style="calm", mode="coach")
            print(f"Guiding: {message}")
