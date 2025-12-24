from typing import Dict, List, NamedTuple

class Strategy(NamedTuple):
    category: str
    title: str
    description: str

STRATEGIES = [
    Strategy(\"sensory_tools\", \"Squeeze Ball\", \"Squeeze a soft ball to release energy.\"),

# ... add more as needed
]

class StrategyAdvisor:
    def suggest(self, event: str) -> List[Strategy]:
        # Simple mapping for now
        if event == \"anxious\":
            return [s for s in STRATEGIES if s.category in [\"mindfulness\", \"sensory_tools\"]]
        # Add more mappings
        return []
