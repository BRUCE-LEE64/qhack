"""
Level 3 — Orthogonality & Expectation Values via Density Matrices
BEVD210L: Quantum Technology for Electronics Engineers
Author: Hariharan Nagarajan (23BVD1005)

Constructs |+⟩ and |−⟩ as density matrices ρ = ½(I + r·σ),
computes Pauli expectation values, and proves orthogonality via Tr(ρ₁ρ₂).
No statevectors are used at any point.
"""

import numpy as np
import matplotlib.pyplot as plt
import qutip as qt

# ─── Density Matrices ─────────────────────────────────────────────────────────

# ρ₁ = |+⟩⟨+|  (Bloch vector r = (+1, 0, 0))
rho1 = qt.Qobj([[0.5,  0.5],
                [0.5,  0.5]])

# ρ₂ = |−⟩⟨−|  (Bloch vector r = (−1, 0, 0))
rho2 = qt.Qobj([[0.5, -0.5],
               [-0.5,  0.5]])

# ─── Pauli Operators ─────────────────────────────────────────────────────────

sigma_x = qt.sigmax()
sigma_y = qt.sigmay()
sigma_z = qt.sigmaz()

# ─── Expectation Values: ⟨σ⟩ = Tr(ρ · σ) ────────────────────────────────────

def expectation(rho, op):
    return (rho * op).tr().real

ev_rho1 = [expectation(rho1, s) for s in [sigma_x, sigma_y, sigma_z]]
ev_rho2 = [expectation(rho2, s) for s in [sigma_x, sigma_y, sigma_z]]

print("Expectation Values:")
print(f"  ρ₁ (|+⟩):  ⟨σx⟩={ev_rho1[0]:+.3f}  ⟨σy⟩={ev_rho1[1]:+.3f}  ⟨σz⟩={ev_rho1[2]:+.3f}")
print(f"  ρ₂ (|−⟩):  ⟨σx⟩={ev_rho2[0]:+.3f}  ⟨σy⟩={ev_rho2[1]:+.3f}  ⟨σz⟩={ev_rho2[2]:+.3f}")

# ─── Orthogonality: Tr(ρ₁ρ₂) ─────────────────────────────────────────────────

overlap = (rho1 * rho2).tr().real
print(f"\nOrthogonality: Tr(ρ₁ρ₂) = {overlap:.6f}")
print("  → States are ORTHOGONAL ✓" if abs(overlap) < 1e-9 else "  → NOT orthogonal ✗")

# ─── Visualisation ────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(15, 5))

# Panel 1: Bloch Sphere
ax_bloch = fig.add_subplot(131, projection='3d')
b = qt.Bloch(fig=fig, axes=ax_bloch)
b.add_states([rho1, rho2])
b.vector_color = ['blue', 'red']
b.render()

# Panel 2: Expectation Values Bar Chart
ax_bar = fig.add_subplot(132)
x = np.arange(3)
width = 0.35
labels = ['⟨σx⟩', '⟨σy⟩', '⟨σz⟩']
ax_bar.bar(x - width/2, ev_rho1, width, label='ρ₁ (|+⟩)', color='blue', alpha=0.7)
ax_bar.bar(x + width/2, ev_rho2, width, label='ρ₂ (|−⟩)', color='red', alpha=0.7)
ax_bar.set_xticks(x)
ax_bar.set_xticklabels(labels)
ax_bar.set_ylim(-1.3, 1.3)
ax_bar.axhline(0, color='black', linewidth=0.5)
ax_bar.set_title('Pauli Expectation Values')
ax_bar.legend()

# Panel 3: Product Matrix Heatmap
ax_heat = fig.add_subplot(133)
product = (rho1 * rho2).full().real
im = ax_heat.imshow(product, cmap='RdBu', vmin=-0.3, vmax=0.3)
ax_heat.set_title(f'ρ₁·ρ₂  (Tr = {overlap:.3f})')
ax_heat.set_xticks([0, 1])
ax_heat.set_yticks([0, 1])
fig.colorbar(im, ax=ax_heat)

plt.tight_layout()
plt.savefig('level3_output.png', dpi=150, bbox_inches='tight')
plt.show()
print("\nPlot saved to level3_output.png")
