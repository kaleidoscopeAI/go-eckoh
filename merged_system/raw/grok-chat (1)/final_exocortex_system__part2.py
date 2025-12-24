import sys
import time
import math
import random
import re

# Utilities
def simulate_audio_input():
    return input("Speak: ").strip()

def correct_to_first_person(text):
    text = text.replace("you", "I").replace("your", "my").capitalize()
    return text

# Autism Metrics: Therapy tracking
class AutismMetrics:
    def __init__(self):
        self.attempts = 0
        self.successes = 0
        self.streak = 0

    def register_attempt(self, success):
        self.attempts += 1
        if success:
            self.successes += 1
            self.streak += 1
        else:
            self.streak = 0

    def success_rate(self):
        return self.successes / self.attempts if self.attempts else 0

# Mindmap Node
class Node:
    def __init__(self):
        self.bits = [random.choice([0, 1]) for _ in range(128)]
        self.position = [random.uniform(-1, 1) for _ in range(3)]
        self.spin = random.choice([-1, 1])
        self.emotion = [0.0] * 5

# Bond Energy
def bond_energy(node1, node2):
    hamming = sum(b1 != b2 for b1, b2 in zip(node1.bits, node2.bits)) / 128
    dist = sum((p1 - p2)**2 for p1, p2 in zip(node1.position, node2.position))
    return 0.5 * hamming + 0.5 * dist

# Entropy for Therapy: Speech disorder (char variance proxy)
def therapy_entropy(text):
    if not text:
        return 0
    codes = [ord(c) for c in text]
    hist = [codes.count(i) for i in set(codes)]
    total = sum(hist)
    p = [h / total for h in hist]
    return -sum(pi * math.log(pi + 1e-10) for pi in p) if p else 0

# Optimized Life Eq: Params from sim [1.0,1.0,1.0]
def life_equation(states, env, past, future, n_copies, dt, lambda1=1.0, lambda2=1.0, lambda3=1.0):
    ds_int = (therapy_entropy(states) - therapy_entropy(past)) / dt if past else 0
    ds_env = random.gauss(0, 0.1)
    term1 = lambda1 * (ds_int - ds_env)

    mi = sum(p * f for p, f in zip(past or [0], future or [0])) / max(len(past), 1)
    h_x = therapy_entropy(states)
    term2 = lambda2 * (mi / (h_x + 1e-10))

    dn = n_copies / dt
    term3 = lambda3 * (dn / (len(states) + 1e-10))

    l = term1 + term2 + term3
    return (math.tanh(l) + 1) / 2

# Crystalline Heart: With therapy entropy + opt life eq
class CrystallineHeart:
    def __init__(self, n_nodes=1024):
        self.nodes = [Node() for _ in range(n_nodes)]
        self.dt = 0.05
        self.history = []

    def step(self, stimulus, text):  # Add text for entropy
        for node in self.nodes:
            drive = stimulus
            decay = -0.5 * sum(node.emotion)
            noise = random.gauss(0, 0.1)
            for i in range(5):
                node.emotion[i] += self.dt * (drive + decay + noise)

        energy = sum(bond_energy(random.choice(self.nodes), random.choice(self.nodes)) for _ in range(100)) / 100

        states = "".join(chr(int(sum(n.emotion) * 10 % 256)) for n in self.nodes)  # Sim "text" from states
        env = "".join(chr(random.randint(0, 255)) for _ in range(self.n_nodes))
        past = self.history[-1] if self.history else states
        future = text + "".join(chr(random.randint(0, 255)) for _ in range(10))  # Sim future with input
        n_copies = self.n_nodes + random.randint(-10, 10)
        gcl = life_equation(states, env, past, future, n_copies, self.dt)

        self.history.append(states)
        if len(self.history) > 10:
            self.history = self.history[-10:]

        therapy_disorder = therapy_entropy(text)  # Entropy as meltdown risk
        return gcl, energy, therapy_disorder

# Deep Reasoning Core
class DeepReasoningCore:
    def __init__(self):
        self.rules = {"help": "I guide: Breathe calm.", "happy": "Joy flows: Well done."}

    def execute(self, text, gcl):
        if gcl > 0.7:
            for key in self.rules:
                if key in text.lower():
                    return self.rules[key]
            return "Reason: Insight unlocked."
        elif gcl > 0.4:
            return "Affirm: Steady."
        else:
            return "Calm: I am safe."

# Auditory-Motor Core
def auditory_motor_core(input_text, metrics):
    corrected = input_text.replace("you", "I").replace("your", "my").capitalize()
    print(f"[Cloned Echo]: {corrected}")
    stimulus = len(input_text) / 10.0
    success = len(corrected) > len(input_text) / 2  # Sim success
    metrics.register_attempt(success)
    return corrected, stimulus

# Final Enhanced Loop
class FinalMergedSystem:
    def __init__(self):
        self.heart = CrystallineHeart()
        self.metrics = AutismMetrics()

    def run(self):
        while True:
            input_text = input("Speak: ").strip()
            if not input_text:
                continue

            echoed, stimulus = auditory_motor_core(input_text, self.metrics)

            gcl, energy, disorder = self.heart.step(stimulus, input_text)

            core = DeepReasoningCore()
            response = core.execute(echoed, gcl)

            print(f"[GCL: {gcl:.2f}] [Energy: {energy:.2f}] [Disorder Entropy: {disorder:.2f}]")
            print(f"[Metrics: Attempts {self.metrics.attempts}, Success {self.metrics.success_rate():.2f}, Streak {self.metrics.streak}]")
            print(f"[Response]: {response}")
            time.sleep(1)

if __name__ == "__main__":
    system = FinalMergedSystem()
    system.run()
