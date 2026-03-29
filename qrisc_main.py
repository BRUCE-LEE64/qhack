"""
qrisc_main.py — Q-RISC++ Entry Point
BEVD210L: Quantum Technology for Electronics Engineers
Author: Hariharan Nagarajan (23BVD1005)

Assembles a quantum error-correction-style test program, runs the Q-RISC++ pipeline
in both forwarding and non-forwarding modes, prints pipeline stats, and plots results.

Test program implements:
  H(QR0) → CNOT(QR0,QR1) → CNOT(QR1,QR2) → CNOT(QR2,QR3) → MEASURE(QR0,CR0)
  → H(QR0) → CNOT(QR0,QR1) → CNOT(QR1,QR2) → MEASURE(QR1,CR1)
  → FEEDBACK(CR1 → QR2) → RZ(QR3, π/4) → MEASURE(QR2,CR2) → MEASURE(QR3,CR3)
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from qrisc_isa import H, X, Y, Z, RZ, RX, CNOT, MEASURE, FEEDBACK, NOP
from qrisc_pipeline import QRISCPipeline

SHOTS = 4096

# ─── Test Program ─────────────────────────────────────────────────────────────

PROGRAM = [
    H(0),
    CNOT(0, 1),
    CNOT(1, 2),
    CNOT(2, 3),
    MEASURE(0, 0),
    H(0),
    CNOT(0, 1),
    CNOT(1, 2),
    MEASURE(1, 1),
    FEEDBACK(1, 2),
    RZ(3, math.pi / 4),
    MEASURE(2, 2),
    MEASURE(3, 3),
]

# ─── Run Both Modes ───────────────────────────────────────────────────────────

def run_mode(use_forwarding: bool):
    label = "WITH Forwarding" if use_forwarding else "WITHOUT Forwarding"
    print(f"\n{'─'*50}")
    print(f"  Mode: {label}")
    print(f"{'─'*50}")
    pipeline = QRISCPipeline(PROGRAM, use_forwarding=use_forwarding)
    stats, ideal_counts, noisy_counts = pipeline.simulate(shots=SHOTS)
    print(f"  Total cycles        : {stats['total_cycles']}")
    print(f"  Real instructions   : {stats['real_instructions']}")
    print(f"  CPI                 : {stats['cpi']:.2f}")
    print(f"  Stalls inserted     : {stats['stalls']}")
    print(f"  Forwarded           : {stats['forwards']}")
    return stats, ideal_counts, noisy_counts, pipeline

# ─── Fidelity Calculation ────────────────────────────────────────────────────

def bhattacharyya_fidelity(ideal: dict, noisy: dict) -> float:
    """Bhattacharyya coefficient between ideal and noisy probability distributions."""
    all_keys = set(ideal) | set(noisy)
    total_ideal = sum(ideal.values())
    total_noisy = sum(noisy.values())
    coeff = 0.0
    for k in all_keys:
        pi = ideal.get(k, 0) / total_ideal
        pn = noisy.get(k, 0) / total_noisy
        coeff += math.sqrt(pi * pn)
    return coeff

# ─── Plotting ─────────────────────────────────────────────────────────────────

def plot_histograms(ideal_nofwd, noisy_nofwd, ideal_fwd, noisy_fwd,
                   fidelity_nofwd, fidelity_fwd):
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))

    def plot_hist(ax, counts, title, color):
        total = sum(counts.values())
        top = sorted(counts.items(), key=lambda x: -x[1])[:10]
        states, cnts = zip(*top) if top else ([], [])
        ax.bar(states, [c / total for c in cnts], color=color, alpha=0.8)
        ax.set_title(title, fontsize=10)
        ax.set_ylabel('Probability')
        ax.tick_params(axis='x', rotation=45)

    plot_hist(axes[0, 0], ideal_nofwd, 'Ideal — No Forwarding', 'steelblue')
    plot_hist(axes[0, 1], noisy_nofwd, f'Noisy — No Forwarding  (Fidelity={fidelity_nofwd:.1%})', 'salmon')
    plot_hist(axes[1, 0], ideal_fwd,   'Ideal — With Forwarding', 'steelblue')
    plot_hist(axes[1, 1], noisy_fwd,   f'Noisy — With Forwarding  (Fidelity={fidelity_fwd:.1%})', 'salmon')

    plt.suptitle('Q-RISC++ Measurement Histograms (4096 shots)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig('level5_histograms.png', dpi=150, bbox_inches='tight')
    plt.show()

def plot_pipeline_comparison(stats_nofwd, stats_fwd):
    metrics = ['Total Cycles', 'CPI', 'Stalls', 'Forwards']
    values_nofwd = [stats_nofwd['total_cycles'], stats_nofwd['cpi'],
                    stats_nofwd['stalls'], stats_nofwd['forwards']]
    values_fwd   = [stats_fwd['total_cycles'],   stats_fwd['cpi'],
                    stats_fwd['stalls'],   stats_fwd['forwards']]

    x = np.arange(len(metrics))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width/2, values_nofwd, width, label='No Forwarding', color='salmon', alpha=0.85)
    ax.bar(x + width/2, values_fwd,   width, label='With Forwarding', color='teal', alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_title('Q-RISC++ Pipeline Performance Comparison')
    ax.legend()
    plt.tight_layout()
    plt.savefig('level5_pipeline_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    stats_nofwd, ideal_nofwd, noisy_nofwd, pipe_nofwd = run_mode(use_forwarding=False)
    stats_fwd,   ideal_fwd,   noisy_fwd,   pipe_fwd   = run_mode(use_forwarding=True)

    fidelity_nofwd = bhattacharyya_fidelity(ideal_nofwd, noisy_nofwd)
    fidelity_fwd   = bhattacharyya_fidelity(ideal_fwd,   noisy_fwd)

    print(f"\n{'─'*50}")
    print("  Fidelity Results")
    print(f"{'─'*50}")
    print(f"  Without Forwarding : {fidelity_nofwd:.1%}")
    print(f"  With Forwarding    : {fidelity_fwd:.1%}")
    print(f"\n  Cycle reduction    : {stats_nofwd['total_cycles'] - stats_fwd['total_cycles']} cycles "
          f"({1 - stats_fwd['total_cycles']/stats_nofwd['total_cycles']:.0%} improvement)")

    plot_histograms(ideal_nofwd, noisy_nofwd, ideal_fwd, noisy_fwd,
                   fidelity_nofwd, fidelity_fwd)
    plot_pipeline_comparison(stats_nofwd, stats_fwd)
    print("\nPlots saved: level5_histograms.png, level5_pipeline_comparison.png")
