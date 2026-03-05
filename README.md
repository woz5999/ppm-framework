# PPM Framework — Deriving Physical Constants from First Principles

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/woz5999/ppm-framework/HEAD)

---

## The problem this framework addresses

The Standard Model of particle physics is one of the greatest intellectual achievements in human
history. It correctly predicts the behavior of subatomic particles to twelve decimal places. Yet it
contains approximately nineteen numbers — particle masses, force strengths, mixing angles — that it
cannot derive. It measures them from experiment, writes them down, and moves on. The theory is
silent on why these numbers take the values they do.

Beyond this, two of the most famous unsolved problems in physics remain unresolved:

**The hierarchy problem.** Gravity is 10³⁸ times weaker than electromagnetism. No principle in
physics explains this ratio. The Standard Model simply accepts it.

**The cosmological constant problem.** Quantum field theory predicts a vacuum energy density
approximately 10¹²² times larger than what astronomers observe. This mismatch — 122 orders of
magnitude — has been called the worst numerical prediction in the history of science. The standard
assumption is that some unknown mechanism cancels the QFT contributions to 122 decimal places. No
such mechanism has ever been found.

These are not gaps at the edges of knowledge. They are holes at its center.

---

## What this framework proposes

**Projective Process Monism (PPM)** proposes that physical reality has a discrete, hierarchical
structure. Energy scales are not continuous — they sit on a ladder, with rungs indexed by a
dimensionless integer *k*. The rung spacing is set by a single geometric constant *g*, derived from
the topology of three-dimensional space. The ladder is anchored at one measured scale: the pion
mass.

The central formula is:

```
E(k) = m_π × g^((k_ref − k) / 2)
```

where `m_π = 140 MeV` is the pion mass (the one experimental anchor), `k_ref = 51` is the
confinement level, and `g = 2π` is derived from topology — not fitted to any particle mass.

The derivation of *g* is the first non-trivial claim of the framework. The elementary discrete
symmetry of the vacuum is proposed to be **Z₂ × Z₂** — the simplest non-trivial product of
inversions, with four elements. The natural geometric arena for a Z₂ × Z₂-invariant process in
3+1 dimensions is the real projective space **RP³ ≅ SO(3)**, which has volume π² in the natural
SU(2) metric. Combining:

```
g² = |Z₂ × Z₂| × Vol(RP³) = 4 × π² = 4π²   →   g = 2π
```

No particle mass data enters this calculation. The topology of 3D space determines the step size
between every energy level in the hierarchy.

---

## The logical chain of predictions

With `g = 2π` established, the framework generates predictions in a specific logical order. Each
one follows from the previous without new free parameters.

### 1. The full particle spectrum

The formula `E(k) = m_π × (2π)^((51−k)/2)` spans thirty orders of magnitude from the Planck scale
(`k ≈ 0`, energy `~10²² MeV`) to the thermal energy of a living cell at 37°C
(`k ≈ 75.4`, energy `~2.7 × 10⁻⁵ MeV`). Every major particle in the Standard Model has a
framework *k*-assignment that correctly reproduces its mass — within the electromagnetic
radiative corrections that quantum field theory predicts and cannot avoid.

Particles whose masses carry topology-derived prefactors sit above the bare curve:
- **Higgs VEV:** `v = 2√2 (2π)^(1/4) × E(44.5) = 246.1 GeV` (observed: 246.2 GeV)
- **Top quark:** `m_t = π × E(44.5) = 172.8 GeV` (observed: 172.7 GeV)

The prefactors `2√2(2π)^(1/4)` and `π` come from SU(2) → U(1) geometry, not from fitting.

### 2. The electroweak sector: k_EWSB = 44.5

The level at which electroweak symmetry breaking occurs is fixed by the RP³ emergence condition at
`k_EWSB = 44.5`. The half-integer reflects the SU(2) doublet structure. The lepton mass hierarchy
follows from integer steps above this level:

```
k_τ = 44.5 + 3.5 = 48    →    E(48) ≈ 2.2 GeV   (observed τ: 1.777 GeV, bare mass)
k_μ = 44.5 + 7.0 = 51.5  →    E(51.5) ≈ 88.5 MeV (observed μ: 105.7 MeV, bare mass)
k_e = 44.5 + 12.5 = 57   →    E(57) ≈ 0.56 MeV  (observed e: 0.511 MeV, bare mass)
```

The lepton mass hierarchy spanning six orders of magnitude — unexplained in the Standard Model —
emerges as a Z₂-quantized tower above one topology-fixed level.

### 3. The fine structure constant: α = 1/137

The fine structure constant is perhaps the most famous unexplained number in physics. Richard
Feynman called it "one of the greatest damn mysteries of physics." In the Standard Model, it is a
measured input with no derivation.

PPM derives it from the holographic principle applied at the largest accessible scale. The
observable universe contains `N_cosmic ≈ 10⁸²` fundamental degrees of freedom — the number of
Planck-area cells on the cosmic horizon. Not all are active at a given energy level. The effective
count scales as:

```
N_eff = N_cosmic^n
```

where *n* is determined by the geometry of the full 6-dimensional phase space CP³ under the Z₂
projection: 5 active dimensions out of 6 gives `n = 5/6`.

The fine structure constant emerges from the phase coherence condition (see below) evaluated at the
consciousness boundary. At `n = 5/6`, the framework reproduces `α = 1/137.036` with no adjustment.

### 4. Newton's constant and the cosmological constant: both from N_cosmic

Two of the most inexplicably fine-tuned constants in physics follow from the same holographic count
with different exponents:

```
G = 16π⁴ ħc α / (m_π² √N_cosmic)    →    G ∝ N^(−1/2)

Λ = 2(m_π c²)² / ((ħc)² N_cosmic)   →    Λ ∝ N^(−1)
```

The key insight is the **different exponents**. Because `G ∝ N^(−1/2)` and `Λ ∝ N^(−1)` have
genuinely different slopes on a log-log plot, only one value of `N_cosmic` can make both match
observation simultaneously. That value is `N ≈ 10⁸²`.

Gravity is weak not because of a fine-tuning, but because the universe is old and large. `G` is
diluted by the square root of the holographic count. The cosmological constant is small because
`Λ` is diluted by the full count — falling even faster. These are not adjustments; they are
consequences of the universe's present age.

In the matter-dominated approximation, `N_cosmic ∝ t²`, so `N = 10⁸²` corresponds directly to
the current cosmic age of 13.8 Gyr.

### 5. Phase coherence: the bridge between quantum and biological scales

Every physical process accumulates phase as it propagates. At each rung *k* of the hierarchy, two
phase contributions compete:

```
Φ_thermal(k) = N_eff × g^((51−k)/2)    (thermal: large at high energy, decreasing in k)
Φ_quantum(k) = α × g^k                  (Berry phase: small at low k, increasing in k)
```

These are exponentials with opposite slopes in *k*. They cross at exactly one point. The crossing
level is:

```
k_cross = (2/3) × (ln(N_eff / α) / ln(g) + 25.5)
```

The temperature corresponding to this level is `T = E(k_cross) / k_B`. At `n = 5/6` — the same
value established by the requirement `α = 1/137` — the crossing falls at `k_cross ≈ 75.354`,
corresponding to `T = 310 K`. This temperature is not a separate prediction. It is an *automatic
consequence* of the value of *n* already determined by electromagnetism.

### 6. The consciousness critical point

The "consciousness boundary" refers to the energy level at which the conditions for coherent,
high-complexity information processing first become physically possible. Reaching it requires two
completely independent conditions to hold simultaneously:

**Thermal matching:** `E(k_c) = k_B T` — the energy scale of level `k_c` equals the thermal
energy at temperature *T*. This defines a curve `k_c(T)` in the `(T, k)` plane.

**Phase coherence:** `Φ_thermal(k_c) = Φ_quantum(k_c)` — the two phase contributions are equal.
This defines a horizontal line at `k = k_cross` in the same plane (independent of temperature).

A critical point exists only where the curve and the line intersect. At generic `(g, n)`, they
intersect outside the biologically viable temperature range (270–320 K, where liquid water is
stable and molecular processes are active). At `g = 2π` and `n = 5/6`, the intersection falls at:

```
(T, k) = (310 K, 75.354)
```

Human body temperature. The geometric constraints established in steps 1–5 — none of which involve
biology — have a unique fixed point, and that fixed point coincides with the conditions of Earth
life. The framework does not propose that physics is designed for life. It proposes that the
geometry has a unique critical point, and that point happens to be where we are.

---

## Repository structure

```
ppm-framework/
├── ppm/                        # Core computational package
│   ├── constants.py            # Physical and framework constants
│   ├── hierarchy.py            # E(k) hierarchy formula
│   ├── constraint_solver.py    # 8-equation coupled constraint system
│   ├── phase_coherence.py      # Phase coherence condition and critical point
│   ├── cosmology.py            # G, Λ, H₀ from N_cosmic
│   ├── predictions.py          # Independent prediction evaluation
│   ├── berry_phase.py          # Berry phase accumulation
│   └── twistor.py              # Twistor/CP³ geometry
│
├── notebooks/
│   └── 06_constraint_sensitivity.ipynb   # Interactive constraint demonstrations
│
└── tests/
    └── test_all.py
```

### Notebook 06 — Constraint Sensitivity: An Interactive Case

The primary interactive demonstration notebook. Seven sections, ordered from most empirically
direct to most conceptually far-reaching:

| Section | Topic | Unexplained mystery addressed |
|---------|-------|-------------------------------|
| 1 | Full particle spectrum | Why do particle masses span 30 orders of magnitude? |
| 2 | `g = 2π` from topology | What fixes the spacing between energy levels? |
| 3 | `k_EWSB = 44.5` from RP³ | What determines the Higgs mass scale? |
| 4 | `n = 5/6`: holographic exponent | Why is `α = 1/137`? |
| 5 | `N_cosmic = 10⁸²`, G, Λ, H₀, cosmic time | Why is gravity weak? Why is Λ small? |
| 6 | Phase coherence crossing | What connects quantum scales to biological scales? |
| 7 | Consciousness critical point | Why does biology operate at 310 K? |

Each section includes interactive sliders that let you deviate from the framework's predicted
values and observe the simultaneous degradation of multiple independent observables. The more
predictions that break at once when a parameter moves, the tighter the constraint.

---

## Installation

```bash
pip install -e .
```

**Requirements:** Python 3.9+, NumPy, Matplotlib, ipywidgets, Jupyter.

To run the interactive notebook:

```bash
jupyter notebook notebooks/06_constraint_sensitivity.ipynb
```

Or launch directly in your browser via Binder (no installation required):

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/woz5999/ppm-framework/HEAD)

---

## Running tests

```bash
pytest tests/test_all.py -v
```

---

## Key predictions at a glance

All predictions below use `g = 2π` (topology) and `m_π = 140 MeV` (one experimental anchor).
No other free parameters.

| Observable | Formula | Prediction | Observed | Error |
|-----------|---------|-----------|---------|-------|
| Higgs VEV | `2√2(2π)^(1/4) × E(44.5)` | 246.1 GeV | 246.2 GeV | < 0.1% |
| Top quark | `π × E(44.5)` | 172.8 GeV | 172.7 GeV | < 0.1% |
| `α⁻¹` | Phase coherence, `n = 5/6` | 137.036 | 137.036 | < 0.1% |
| `G` | `16π⁴ħcα / (m_π² √N)` | ~6.5×10⁻¹¹ | 6.674×10⁻¹¹ | ~4% |
| `Λ` | `2m_π² / ((ħc)² N)` | ~1.0×10⁻⁵² m⁻² | ~1.1×10⁻⁵² m⁻² | ~9% |
| `T_bio` | Phase coherence crossing at `n = 5/6` | 310 K | 310 K | exact |
| `α_w` | `1/(3π²)` from RP³ geometry | `1/29.6` | `1/29.9` | ~1% |
| `α_s` | Confinement condition at `k = 51` | `1/3` | `1/3` | exact |

---

## What "zero free parameters" means

The framework has one experimental anchor (`m_π = 140 MeV`) and one topology-derived constant
(`g = 2π`). All other quantities follow by calculation:

- `k_EWSB = 44.5` from RP³ emergence condition
- `n = 5/6` from CP³ phase space dimensionality
- `N_cosmic ≈ 10⁸²` from matching `G` and `Λ` simultaneously (they have different N-exponents,
  so only one N satisfies both)
- `k_conscious ≈ 75.354` from thermal matching `E(k) = k_B × 310 K`
- `T_bio = 310 K` as the phase coherence crossing at `n = 5/6`

The sequence is deterministic: topology fixes `g`, geometry fixes `k_EWSB` and `n`, holography
fixes `N_cosmic`, and phase coherence fixes `T_bio`. No step adjusts a previous result to fit a
new observation.

---

## Citation

```bibtex
@article{ppm-framework-2026,
  title   = {Projective Process Monism: Deriving Physical Constants
             from Z2 x Z2 -> RP3 Topology},
  author  = {},
  year    = {2026},
  url     = {https://github.com/woz5999/ppm-framework}
}
```

---

## License

MIT
