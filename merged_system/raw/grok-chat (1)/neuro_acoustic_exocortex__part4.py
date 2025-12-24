import sys
import time
import math
import random

# Utilities: String methods for correction
def simulate_audio_input():
    return input("Speak (type phrase): ").strip()

def correct_to_first_person(text):
    # Pure string: Replace "you" with "I", etc.
    text = text.replace(" you ", " I ").replace(" your ", " my ")
    return text[0].upper() + text[1:]

# Crystalline Heart: ODE lattice for GCL
class CrystallineHeart:
    def __init__(self, n_nodes=1024):
        self.n_nodes = n_nodes
        self.states = [random.uniform(-1, 1) for _ in range(n_nodes)]
        self.dt = 0.05

    def step(self, arousal, latency):
        # Stimulus: Arousal from length, latency sim stress
        stimulus = arousal - latency  # Net affect

        # Update: Simplified ODE (no matrix for pure)
        for i in range(self.n_nodes):
            drive = stimulus
            decay = -0.5 * self.states[i]
            noise = random.uniform(-0.1, 0.1)
            ds = drive + decay + noise
            self.states[i] += self.dt * ds

        # GCL: Tanh mean (0-1 normalize)
        gcl = (sum(math.tanh(s) for s in self.states) / self.n_nodes + 1) / 2
        return gcl

# Deep Reasoning Core: Gated strategies
class DeepReasoningCore:
    def __init__(self):
        self.strategies = {
            "green": "Deep plan: Let's advance that skill.",
            "yellow": "Simple guide: Steady now.",
            "red": "Calm affirm: I am safe, breathe."
        }

    def execute(self, text, gcl):
        if gcl > 0.7:  # GREEN
            return self.strategies["green"]
        elif gcl > 0.5:  # YELLOW (0.5-0.7 per query)
            return self.strategies["yellow"]
        else:  # RED
            return self.strategies["red"]

# Auditory-Motor Core: Mirror with CD Proxy
def auditory_motor_core(input_text):
    corrected = correct_to_first_person(input_text)
    print(f"[Cloned Voice Echo]: {corrected}")
    arousal = len(input_text) / 20.0  # Sim energy
    latency = random.uniform(0, 0.5)  # Sim clarity error
    return corrected, arousal, latency

# Main Loop: Closed triad
class NeuroAcousticExocortex:
    def __init__(self):
        self.heart = CrystallineHeart()
        self.drc = DeepReasoningCore()

    def run(self):
        while True:
            input_text = simulate_audio_input()
            if not input_text:
                continue

            echoed, arousal, latency = auditory_motor_core(input_text)

            gcl = self.heart.step(arousal, latency)

            response = self.drc.execute(echoed, gcl)

            print(f"[GCL: {gcl:.2f}] [Gated Response]: {response}")
            time.sleep(1)

if __name__ == "__main__":
    exocortex = NeuroAcousticExocortex()
    exocortex.run()
