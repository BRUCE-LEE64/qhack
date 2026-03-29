# QHack Levels 1-5

> **Author:** Hariharan Nagarajan
> **Platform:** Qiskit / Qiskit Aer / QuTiP
> **Tools:** Python 3.11 · Jupyter Notebook

---

## 📦 Repository Structure

```
qhack/
├── level1_ripple_carry_adder/   # 4-bit quantum ripple carry adder (MAJ/UMA)
├── level2_priority_encoder/     # Quantum priority encoder / emergency selector
├── level3_density_matrices/     # Density matrix orthogonality & Pauli expectation values
├── level4_bb84_qkd/             # BB84 QKD with adaptive eavesdropper simulation
├── level5_qriscc/               # Q-RISC++: Pipelined quantum processor simulator
└── README.md
```

---

## 🗺️ Level Overview

| Level | Topic | Platform | Key Concept |
|-------|-------|----------|-------------|
| [1](./level1_ripple_carry_adder) | 4-Bit Ripple Carry Adder | Qiskit Aer | Reversible quantum arithmetic with MAJ/UMA gate decomposition |
| [2](./level2_priority_encoder) | Quantum Priority Encoder | Qiskit Aer | Multi-controlled gate logic encoding classical priority circuits |
| [3](./level3_density_matrices) | Density Matrix Orthogonality | QuTiP | Quantum state characterisation via Tr(ρ₁ρ₂), Bloch vectors, Pauli expectation values |
| [4](./level4_bb84_qkd) | BB84 QKD + Adaptive Eve | Qiskit Aer + Noise Model | Quantum cryptography with realistic noise and adaptive eavesdropper strategy |
| [5](./level5_qriscc) | Q-RISC++ Pipelined Processor | Qiskit Aer + IBM Eagle r3 | Classical RISC pipeline architecture applied to a quantum ISA |

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.11+
- Jupyter Notebook or JupyterLab

### Install Dependencies

```bash
pip install qiskit qiskit-aer qutip matplotlib numpy
```

Or install from the requirements file:

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Notebooks

Each level is self-contained. Navigate to the relevant folder and launch Jupyter:

```bash
cd level1_ripple_carry_adder
jupyter notebook level1_ripple_carry_adder.ipynb
```

All notebooks are designed to run top-to-bottom without modification.

---

## 📋 Requirements

See [`requirements.txt`](./requirements.txt) for the full dependency list.

---

## 📄 License

This project is submitted as coursework for BEVD210L — Quantum Technology for Electronics Engineers.
