"""
import sys
import time
import random
from typing import List, Optional
import torch
import networkx as nx
import sympy as sp
from sympy.solvers.ode import dsolve
# Optional: torchdiffeq for better ODE integration
try:
    from torchdiffeq import odeint
    HAS_TORCHDIFFEQ = True
except ImportError:
    HAS_TORCHDIFFEQ = False
# ---------------------------------------------------------------------
# Self-correction decorator
# ---------------------------------------------------------------------
def self_correcting(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator: retry a function a few times before giving up.
    Prints soft errors, then raises RuntimeError on persistent failure.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exc: Optional[Exception] = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    print(
                        f"[SELF-CORRECT] Error in {func.__name__}: {e}. "
                        f"Retrying {attempt + 1}/{max_retries}..."
                    )
                    time.sleep(delay)
            raise RuntimeError(
                f"Failed after {max_retries} retries in {func.__name__}"
            ) from last_exc
        return wrapper
    return decorator
# ---------------------------------------------------------------------
# Symbolic emotional ODE (for reference / future analysis)
# ---------------------------------------------------------------------
t, E, a, b, c, input_sym = sp.symbols("t E a b c input")
emotional_ode = sp.Eq(sp.diff(E, t), a * E - b * E**2 + c * input_sym)
try:
    emotional_solution = dsolve(emotional_ode, E)
except Exception as e:
    print(f"[WARN] Symbolic solve failed: {e}. Using numerical method only.")
    emotional_solution = None
# ---------------------------------------------------------------------
# Main system
# ---------------------------------------------------------------------
class ConsciousCrystalSystem:
    """
    A simple "crystal mind":
    - Nodes in a graph, each with an energy value.
    - Energy evolves via a logistic-like ODE with external input.
    - Nodes with high energy replicate.
    - System self-reflects and tweaks parameters / topology.
    """
    def __init__(
        self,
        num_nodes: int = 10,
        energy_threshold: float = 5.0,
        replication_rate: float = 0.1,
    ):
        self.graph = self._initialize_graph(num_nodes)
        # Energies aligned to node indices [0..num_nodes-1]
        self.energies = torch.tensor(
            [random.uniform(0.0, 10.0) for _ in range(num_nodes)],
            dtype=torch.float32,
        )
        self.energy_threshold = float(energy_threshold)
        self.replication_rate = float(replication_rate)
        # ODE parameters
        self.params = {"a": 1.0, "b": 0.1, "c": 0.5}
        # History of mean energy (for reflection)
        self.history: List[float] = []
    # -----------------------------------------------------------------
    # Structure
    # -----------------------------------------------------------------
    @self_correcting()
    def _initialize_graph(self, num_nodes: int) -> nx.Graph:
        """
        Create a sparse random graph and ensure it's connected.
        """
        G = nx.Graph()
        for i in range(num_nodes):
            G.add_node(i)
        # Random sparse edges
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if random.random() < 0.3:
                    G.add_edge(i, j)
        # Ensure connectivity (if there are multiple components)
        if not nx.is_connected(G):
            components = [list(c) for c in nx.connected_components(G)]
            base_component = components[0]
            for comp in components[1:]:
                u = random.choice(base_component)
                v = random.choice(comp)
                G.add_edge(u, v)
        return G
    # -----------------------------------------------------------------
    # Dynamics
    # -----------------------------------------------------------------
    @self_correcting()
    def update_energies(self, inputs: torch.Tensor, dt: float = 0.1) -> None:
        """
        Update node energies by integrating the ODE dE/dt = aE - bE^2 + c*input.
        inputs: tensor of shape [num_nodes]
        dt: time-step length
        """
        inputs = torch.as_tensor(inputs, dtype=self.energies.dtype)
        if inputs.shape != self.energies.shape:
            raise ValueError(
                f"inputs shape {inputs.shape} does not match energies {self.energies.shape}"
            )
        def ode_func(_t, y):
            return (
                self.params["a"] * y
                - self.params["b"] * y**2
                + self.params["c"] * inputs
            )
        if HAS_TORCHDIFFEQ:
            t_span = torch.tensor([0.0, float(dt)], dtype=self.energies.dtype)
            new_energies = odeint(ode_func, self.energies, t_span)[-1]
        else:
            # Simple explicit Euler fallback
            new_energies = self.energies + dt * ode_func(0.0, self.energies)
        # Clamp to non-negative
        self.energies = new_energies.clamp(min=0.0)
        # Log for reflection
        self.history.append(self.energies.mean().item())
    # -----------------------------------------------------------------
    # Replication
    # -----------------------------------------------------------------
    @self_correcting()
    def replicate_nodes(self) -> None:
        """
        Nodes whose energy exceeds threshold spawn a new child node.
        Parent retains most of its energy; a small fraction seeds the child.
        """
        new_nodes: List[int] = []
        current_nodes = list(self.graph.nodes)
        for node in current_nodes:
            if self.energies[node] > self.energy_threshold:
                new_node = self.graph.number_of_nodes()
                self.graph.add_node(new_node)
                self.graph.add_edge(node, new_node)
                child_energy = self.energies[node] * self.replication_rate
                self.energies = torch.cat(
                    [self.energies, child_energy.unsqueeze(0)]
                )
                self.energies[node] *= (1.0 - self.replication_rate)
                new_nodes.append(new_node)
        if new_nodes:
            print(f"[REPLICATION] New nodes: {new_nodes}")
    # -----------------------------------------------------------------
    # Self-reflection
    # -----------------------------------------------------------------
    @self_correcting()
    def self_reflect(self) -> None:
        """
        Look at history and graph structure, then tweak parameters or topology.
        """
        if len(self.history) <= 1:
            print("[REFLECT] Insufficient history for reflection.")
            return
        growth = self.history[-1] - self.history[0]
        # If global energy falling, increase growth rate 'a'
        if growth < 0.0:
            print("[REFLECT] Energy decreasing. Adjusting 'a' up slightly.")
            self.params["a"] += 0.1
        # If clustering is too low, add random edges
        clustering = nx.average_clustering(self.graph)
        if clustering < 0.2:
            print("[REFLECT] Low clustering. Adding edges for stability...")
            nodes = list(self.graph.nodes)
            for _ in range(max(1, len(nodes) // 2)):
                i, j = random.sample(nodes, 2)
                if not self.graph.has_edge(i, j):
                    self.graph.add_edge(i, j)
    # -----------------------------------------------------------------
    # Simulation
    # -----------------------------------------------------------------
    @self_correcting()
    def simulate(self, steps: int = 10) -> None:
        """
        Run the system for N steps with random external input each time.
        """
        num_nodes = self.graph.number_of_nodes()
        for step in range(steps):
            # Generate random inputs aligned to current node count
            inputs = torch.tensor(
                [random.uniform(-1.0, 1.0) for _ in range(num_nodes)],
                dtype=self.energies.dtype,
            )
            print(
                f"[STEP {step:03d}] "
                f"mean_energy = {self.energies.mean().item():.3f}, "
                f"nodes = {self.graph.number_of_nodes()}"
            )
            self.update_energies(inputs)
            self.replicate_nodes()
            self.self_reflect()
            # Update node count for next iteration
            num_nodes = self.graph.number_of_nodes()
# ---------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------
if __name__ == "__main__":
    try:
        system = ConsciousCrystalSystem()
        system.simulate(steps=20)
    except Exception as e:
        print(f"[FATAL] Critical system error: {e}. Initiating shutdown.")
        sys.exit(1)
