import sys
import time
import math
import random
import re  # Built-in for patterns

# Mindmap: Atomic/Node Level - Bits, genomes, positions
class Node:
    def __init__(self):
        self.bits = [random.choice([0, 1]) for _ in range(128)]  # Genome
        self.position = [random.uniform(-1, 1) for _ in range(3)]  # 3D
        self.spin = random.choice([-1, 1])  # Ising
        self.emotion = [0.0] * 5  # Arousal, valence, etc.

# Mindmap: Bond/Interaction - Hamming + spatial
def bond_energy(node1, node2):
    hamming = sum(b1 != b2 for b1, b2 in zip(node1.bits, node2.bits)) / 128
    dist = sum((p1 - p2)**2 for p1, p2 in zip(node1.position, node2.position))
    return 0.5 * hamming + 0.5 * dist

# Life Equation: In Heart for GCL
def life_equation(states, env, past, future, n_copies, dt):
    ds_int = (entropy(states) - entropy(past)) / dt if past else 0
    ds_env = random.gauss(0, 0.1)
    term1 = ds_int - ds_env

    mi = mutual_info(past, future)
    h_x = entropy(states)
    term2 = mi / (h_x + 1e-10) if h_x else 0

    dn = n_copies / dt
    term3 = dn / (len(states) + 1e-10)

    l = 0.4 * term1 + 0.3 * term2 + 0.3 * term3
    return (math.tanh(l) + 1) / 2  # Normalize 0-1

def entropy(values):
    if not values:
        return 0
    hist = [math.exp(-v**2) for v in values]  # Approx
    total = sum(hist)
    p = [h / total for h in hist]
    return -sum(pi * math.log(pi + 1e-10) for pi in p)

def mutual_info(past, future):
    return sum(p * f for p, f in zip(past or [0], future or [0])) / max(len(past), 1)

# Crystalline Heart: ODE + Life Eq for GCL
class CrystallineHeart:
    def __init__(self, n_nodes=1024):
        self.nodes = [Node() for _ in range(n_nodes)]
        self.dt = 0.05
        self.history = []

    def step(self, stimulus):
        # ODE: Update emotions
        for node in self.nodes:
            drive = stimulus
            decay = -0.5 * sum(node.emotion)
            noise = random.gauss(0, 0.1)
            for i in range(5):
                node.emotion[i] += self.dt * (drive + decay + noise)

        # Bonds/Energy: Sim hamiltonian
        energy = sum(bond_energy(random.choice(self.nodes), random.choice(self.nodes)) for _ in range(100)) / 100

        # Life Eq for GCL
        states = [sum(n.emotion) for n in self.nodes]
        env = [random.uniform(-1, 1) for _ in range(self.n_nodes)]
        past = self.history[-1] if self.history else states
        future = [s + random.gauss(0, 0.1) for s in states]  # Sim
        n_copies = self.n_nodes + random.randint(-10, 10)  # Growth sim
        gcl = life_equation(states, env, past, future, n_copies, self.dt)

        self.history.append(states)
        if len(self.history) > 10:
            self.history = self.history[-10:]

        return gcl, energy

# Deep Reasoning Core: Gated by GCL
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

# Auditory-Motor Core: Mirror with first-person CD Proxy
def auditory_motor_core(input_text):
    corrected = input_text.replace("you", "I").replace("your", "my").capitalize()
    print(f"[Cloned Echo]: {corrected}")
    stimulus = len(input_text) / 10.0
    return corrected, stimulus

# Final Merged Loop: Exocortex + Mindmap + Life Eq
class FinalMergedSystem:
    def __init__(self):
        self.heart = CrystallineHeart()

    def run(self):
        while True:
            input_text = input("Speak: ").strip()
            if not input_text:
                continue

            echoed, stimulus = auditory_motor_core(input_text)

            gcl, energy = self.heart.step(stimulus)

            core = DeepReasoningCore()
            response = core.execute(echoed, gcl)

            print(f"[GCL: {gcl:.2f}] [Energy: {energy:.2f}] [Response]: {response}")
            time.sleep(1)

if __name__ == "__main__":
    system = FinalMergedSystem()
    system.run()
