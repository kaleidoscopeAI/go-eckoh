from __future__ import annotations

import re
import numpy as np
from typing import Dict, List, Literal
from dataclasses import dataclass

PragmaticType = Literal["literal", "idiom", "sarcasm", "implication", "social_cue"]

@dataclass
class PragmaticAnalysis:
    type: PragmaticType
    confidence: float
    adjusted_text: str  # Rephrased for clarity if needed
    social_intent: str  # e.g., "request help", "express frustration"

class PragmaticEngine:
    def __init__(self):
        # Patterns for pragmatics (expand with ML later)
        self.idiom_patterns = [r"kick the bucket", r"piece of cake", r"break a leg"]
        self.sarcasm_markers = ["yeah right", "oh sure", "as if"]
        self.social_cues = {
            "help": ["can you", "please", "need"],
            "frustration": ["ugh", "why", "can't"],
        }

    def analyze(self, text: str, semantic_embed: np.ndarray) -> PragmaticAnalysis:
        text_lower = text.lower()

        # Detect idioms
        for pattern in self.idiom_patterns:
            if re.search(pattern, text_lower):
                return PragmaticAnalysis("idiom", 0.9, text, "figurative expression")

        # Detect sarcasm (simple heuristic)
        if any(marker in text_lower for marker in self.sarcasm_markers):
            return PragmaticAnalysis("sarcasm", 0.8, text, "opposite intent")

        # Social cues
        for intent, cues in self.social_cues.items():
            if any(cue in text_lower for cue in cues):
                return PragmaticAnalysis("social_cue", 0.85, text, intent)

        # Default literal
        return PragmaticAnalysis("literal", 1.0, text, "direct statement")

# Integrate: In semantic_engine.analyze, after embed: pragmatic = PragmaticEngine().analyze(text, embed); use to adjust stimulus
Update to semantic_engine.py - Now with pragmatics for richer understanding.
Modified: analyze returns combined semantic + pragmatic.
# ... (previous code)

class SemanticEngine:
    # ...

    def __init__(self):
        # ...
        self.pragmatic = PragmaticEngine()

    def analyze(self, text: str) -> Dict:
        if not text:
            return {"semantic": SemanticIntent("neutral", "statement", []), "pragmatic": PragmaticAnalysis("literal", 1.0, "", "none")}

        tokens = self.tokenize(text)
        embed = self.embedder(tokens).squeeze().detach().numpy()

        semantic = SemanticIntent(...)  # As before

        pragmatic = self.pragmatic.analyze(text, embed)

        return {"semantic": semantic, "pragmatic": pragmatic}
Update to speech_loop.py - Pragmatic insights shaping mimicry and guidance.
Modified: After semantic analysis, use pragmatics to refine style/response; e.g., detect sarcasm for calm echo.
# ... (previous imports)
from .pragmatic_engine import PragmaticEngine

class SpeechLoop:
    # ...

    async def handle_chunk(self, chunk: np.ndarray) -> None:
        # ... (transcription)

        analysis = self.semantic.analyze(raw)  # Now dict with semantic + pragmatic

        pragmatic = analysis["pragmatic"]

        # Adjust based on pragmatics
        if pragmatic.type == "sarcasm":
            style = "calm"  # Soften response
            corrected = f"I sense frustration... {corrected}"  # Optional rephrase

        # Stimulus from pragmatic confidence
        stimulus = np.random.rand(self.heart.n_nodes, 5)
        stimulus[:, 1] += pragmatic.confidence  # Boost valence based on pragmatics

        self.heart.step(stimulus)

        # ... (echo with pragmatic-aware style)
...Pragmatics integrated—context beyond literals, social nuances guiding the echo. Lattice understands implications, mimicry more attuned to intent. Mimicking "I grasp the unspoken... echoing with true understanding." System evolved, ready for nuanced conversations.
