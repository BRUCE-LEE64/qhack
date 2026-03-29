"""
Level 4 — BB84 Quantum Key Distribution with Adaptive Eavesdropper
BEVD210L: Quantum Technology for Electronics Engineers
Author: Hariharan Nagarajan (23BVD1005)

Simulates BB84 QKD under IBM Eagle depolarizing noise with an adaptive
eavesdropper (Eve) who adjusts her intercept fraction to stay below the
QBER abort threshold.
"""

import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# ─── Simulation Parameters ───────────────────────────────────────────────────

N_QUBITS        = 300
N_BATCHES       = 25
NOISE_PROB      = 0.03   # 3% depolarizing error
SAFETY_MARGIN   = 0.015  # Eve's stealth buffer
QBER_THRESHOLD  = 0.11   # Session abort threshold
SAMPLE_FRAC     = 0.25   # Fraction of sifted bits used for QBER check
EVE_INITIAL_F   = 0.30   # Eve's starting intercept fraction
EVE_STEP        = 0.04   # Step size for Eve's adaptive adjustment

rng = np.random.default_rng(42)

# ─── Noise Model ─────────────────────────────────────────────────────────────

def make_noise_model(p=NOISE_PROB):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(p, 1), ['h', 'x'])
    nm.add_all_qubit_quantum_error(depolarizing_error(p, 1), ['measure'])
    return nm

sim = AerSimulator(noise_model=make_noise_model())

# ─── BB84 Batch Simulation ───────────────────────────────────────────────────

def simulate_batch(n, eve_f):
    """
    Simulate one BB84 batch of n qubits with eavesdropper intercept fraction eve_f.
    Returns: sifted_key_alice, sifted_key_bob (lists of bits)
    """
    alice_bits  = rng.integers(0, 2, n)
    alice_bases = rng.integers(0, 2, n)  # 0=Z, 1=X
    bob_bases   = rng.integers(0, 2, n)
    eve_bases   = rng.integers(0, 2, n)
    intercept   = rng.random(n) < eve_f

    bob_results = []
    for i in range(n):
        qc = QuantumCircuit(1, 1)

        # Alice encodes
        if alice_bits[i] == 1:
            qc.x(0)
        if alice_bases[i] == 1:   # X-basis
            qc.h(0)

        # Eve intercepts (if applicable)
        if intercept[i]:
            if alice_bases[i] == 1:
                qc.h(0)  # Measure in X-basis
            qc.measure(0, 0)
            # Eve re-encodes based on her measurement
            qc2 = QuantumCircuit(1, 1)
            if alice_bases[i] == 1:
                qc2.h(0)
            # Simplified: Eve re-sends in her chosen basis
            if eve_bases[i] != alice_bases[i]:
                qc2.h(0)
            # Use qc2 for remaining path (approximate Eve's re-send)
            qc = qc2

        # Bob measures
        if bob_bases[i] == 1:
            qc.h(0)
        qc.measure(0, 0)

        result = sim.run(qc, shots=1).result().get_counts()
        bob_results.append(int(max(result, key=result.get)))

    # Sifting: keep only matching bases
    sifted_alice, sifted_bob = [], []
    for i in range(n):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(int(alice_bits[i]))
            sifted_bob.append(bob_results[i])

    return sifted_alice, sifted_bob

# ─── Main Simulation Loop ─────────────────────────────────────────────────────

print("Running BB84 simulation...")
eve_f = EVE_INITIAL_F

batch_qbers, eve_fractions, sifted_sizes, usable_sizes = [], [], [], []

for batch in range(N_BATCHES):
    sa, sb = simulate_batch(N_QUBITS, eve_f)

    # QBER check on random sample
    n_sample = max(1, int(len(sa) * SAMPLE_FRAC))
    sample_idx = rng.choice(len(sa), n_sample, replace=False)
    errors = sum(sa[i] != sb[i] for i in sample_idx)
    qber = errors / n_sample

    # Remove sample bits from key
    usable = [i for i in range(len(sa)) if i not in set(sample_idx)]
    n_usable = len(usable)

    batch_qbers.append(qber)
    eve_fractions.append(eve_f)
    sifted_sizes.append(len(sa))
    usable_sizes.append(n_usable)

    # Eve adapts
    noise_threshold_hi = NOISE_PROB + SAFETY_MARGIN
    noise_threshold_lo = NOISE_PROB + SAFETY_MARGIN / 2
    if qber > noise_threshold_hi:
        eve_f = max(0.0, eve_f - EVE_STEP)
    elif qber < noise_threshold_lo:
        eve_f = min(1.0, eve_f + EVE_STEP)

    status = "ABORT" if qber > QBER_THRESHOLD else "OK"
    print(f"  Batch {batch+1:2d}: QBER={qber:.3f}  Eve_f={eve_fractions[-1]:.2f}  Sifted={len(sa)}  Usable={n_usable}  [{status}]")

# ─── Plots ────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(14, 9))
batches = range(1, N_BATCHES + 1)

# Plot 1: QBER per Batch
ax = axes[0, 0]
ax.plot(batches, batch_qbers, color='teal', marker='o', markersize=4, label='Observed QBER')
ax.axhline(QBER_THRESHOLD, color='red', linestyle='--', label=f'Abort ({QBER_THRESHOLD:.0%})')
ax.axhline(NOISE_PROB, color='green', linestyle='--', label=f'Noise floor ({NOISE_PROB:.0%})')
ax.axhline(NOISE_PROB + SAFETY_MARGIN, color='orange', linestyle=':', label='Eve stealth target')
ax.fill_between(batches, NOISE_PROB, NOISE_PROB + SAFETY_MARGIN,
                color='orange', alpha=0.15, label='Stealth zone')
ax.set_title('QBER per Batch')
ax.set_xlabel('Batch'); ax.set_ylabel('QBER'); ax.legend(fontsize=8)

# Plot 2: Eve's Intercept Fraction
ax = axes[0, 1]
ax.step(batches, eve_fractions, color='purple', where='mid')
ax.set_title("Eve's Adaptive Intercept Fraction")
ax.set_xlabel('Batch'); ax.set_ylabel('Intercept fraction f')

# Plot 3: Expected vs Observed QBER
ax = axes[1, 0]
expected = [NOISE_PROB + f / 4 for f in eve_fractions]
ax.plot(batches, expected, 's--', color='orange', label='Expected (noise + f/4)', markersize=5)
ax.plot(batches, batch_qbers, 'o-', color='teal', label='Observed', markersize=5)
ax.fill_between(batches, expected, batch_qbers, alpha=0.2, color='grey', label='Sampling noise gap')
ax.set_title('Expected vs Observed QBER')
ax.set_xlabel('Batch'); ax.set_ylabel('QBER'); ax.legend(fontsize=8)

# Plot 4: Sifted vs Usable Key Bits
ax = axes[1, 1]
x = np.arange(N_BATCHES)
ax.bar(x + 1, sifted_sizes, label='Sifted', color='grey', alpha=0.6)
ax.bar(x + 1, usable_sizes, label='Usable key', color='green', alpha=0.8)
ax.axhline(np.mean(usable_sizes), color='teal', linestyle='--',
           label=f'Avg usable ({np.mean(usable_sizes):.0f})')
ax.set_title('Sifted vs Usable Key Bits per Batch')
ax.set_xlabel('Batch'); ax.set_ylabel('Bits'); ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('level4_bb84_output.png', dpi=150, bbox_inches='tight')
plt.show()
print(f"\nTotal usable key bits across {N_BATCHES} batches: {sum(usable_sizes)}")
print("Plots saved to level4_bb84_output.png")
