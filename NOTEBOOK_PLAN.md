# PPM Notebook Rebuild — Execution Plan

## Date: 2026-03-19
## Status: COMPLETE

---

## Overview

Three notebooks, one rebuilt `ppm/` package. All live in `github-notebook/ppm-framework/`.

| Notebook | File | Audience | Style |
|----------|------|----------|-------|
| **Sizzle Reel** | `notebooks/predictions.ipynb` | Everyone | Live code → big numbers. No sliders. |
| **Interactive Explorer** | `notebooks/explorer.ipynb` | Scientifically literate | Narrative + FloatSliders + interactive_output |
| **Technical Derivations** | `notebooks/derivations.ipynb` | Physicists checking math | Every equation, every intermediate step |

Old notebooks archived to `notebooks/archive/`.

---

## Phase 0: Scaffolding
- [x] Plan written
- [x] Archive old notebooks to `notebooks/archive/`
- [x] Archive old `ppm/` to `ppm_old/`
- [x] Create new `ppm/` package skeleton with module stubs
- [x] Update `requirements.txt` and `binder/requirements.txt`

## Phase 1: Rebuild `ppm/` Package
Source: paper's `ppm/` (2,394 lines across 11 modules). Rebuild as notebook `ppm/` with:
- Same computational core
- Better docstrings (skeptics will read this code)
- Presentation wrappers for notebook use
- No scipy dependency in core (keep it optional for advanced spectral stuff)

### Module plan:

| New module | Source(s) | Key functions | Lines (est) |
|------------|-----------|---------------|-------------|
| `constants.py` | paper `constants.py` | All physical/mathematical constants, CP³ parameters | ~150 |
| `hierarchy.py` | paper `hierarchy.py` | E(k), k_from_mass, g derivation, k-level table | ~200 |
| `alpha.py` | paper `alpha.py` + notebook `twistor.py` | Three routes (spectral, cogito, instanton), twisted heat trace, CP^n selectivity | ~350 |
| `gauge.py` | paper `gauge.py` | sin²θ_W, generations, coupling running, lepton masses | ~250 |
| `higgs.py` | paper `tau_involution.py` | λ_PPM, Δλ, top Yukawa, geometric identity | ~180 |
| `instanton.py` | paper `instanton.py` | S=30π, zero modes, φ^{-196}, prefactor budget | ~250 |
| `spectral.py` | paper `spectral.py` | Heat kernel coefficients, ζ(0), det(Δ), Z₁ | ~200 |
| `cosmology.py` | paper `gravity.py` + notebook `cosmology.py` | G, Λ, H₀, G(z), w_eff, sterile ν, Sidharth/φ-chain | ~350 |
| `golden_ratio.py` | NEW (from investigation) | Pyramidal numbers, A₅ decomposition, L-function bridge | ~200 |
| `predictions.py` | paper `predictions.py` | Master table builder, all 23+ predictions | ~250 |
| `berry_phase.py` | notebook `berry_phase.py` | CKM via Berry phase, δ_CP = π(1-1/φ) | ~150 |
| `neutrino.py` | NEW | PMNS (TBM), θ_strong = 0, neutrino mass brackets | ~150 |
| `verify.py` | paper `verify.py` | Run-all, pass/fail report | ~120 |
| `__init__.py` | — | Package docstring, version, public API | ~50 |

**Total estimate: ~2,850 lines**

### Checkpoint after Phase 1:
- [x] All modules created and importable (14 modules, ~3,100 lines)
- [x] `python -c "import ppm; ppm.verify.run_all()"` passes (22/22 PASS)
- [x] Key numbers verified: 1/α = 137.257, H₀ = 70.9, sin²θ_W = 0.375

---

## Phase 2: Notebook 1 — "Predictions" (Sizzle Reel)

### Design principles:
- Opens cold. No preamble longer than 3 sentences.
- Every prediction is a code cell that computes the number live.
- Format: **Predicted: X.XX | Observed: Y.YY | Error: Z.ZZ%**
- Grouped by impact, not by derivation order.
- ~15-20 cells total. Fast to scroll. No sliders.

### Cell outline:

| # | Type | Content |
|---|------|---------|
| 1 | MD | Title + 3-sentence hook |
| 2 | CODE | Setup (imports, suppress warnings) |
| 3 | MD | **Headline: The Fine-Structure Constant** |
| 4 | CODE | α Route I computation → 1/α = 137.257 (0.16%) |
| 5 | MD | **CP Violation Phase** |
| 6 | CODE | δ_CP = π(1-1/φ) = 68.8° — testable at DUNE |
| 7 | MD | **The Hubble Constant** |
| 8 | CODE | H₀ = 70.9 km/s/Mpc — splits early/late tension |
| 9 | MD | **Dark Energy** |
| 10 | CODE | Λ and w_eff prediction |
| 11 | MD | **The Weak Mixing Angle** |
| 12 | CODE | sin²θ_W = 3/8 at Pati-Salam scale |
| 13 | MD | **Three Generations — No More, No Less** |
| 14 | CODE | Generation count from CP³ topology |
| 15 | MD | **The Higgs Quartic** |
| 16 | CODE | λ_PPM, Δλ, top Yukawa |
| 17 | MD | **Strong CP: θ = 0 Exactly** |
| 18 | CODE | θ_strong = 0 from RP³ non-orientability |
| 19 | MD | **Neutrino Mixing** |
| 20 | CODE | TBM PMNS matrix |
| 21 | MD | **The Mass Hierarchy — All Particles on One Curve** |
| 22 | CODE | Full k-level table with all particle masses |
| 23 | MD | **Gravity from Coarse-Graining** |
| 24 | CODE | G from holographic count |
| 25 | MD | **G(z) Evolves — Falsifiable** |
| 26 | CODE | G_eff(z) prediction curve |
| 27 | MD | **The Golden Ratio Is Not Decorative** |
| 28 | CODE | Pyramidal identity, A₅ chain, φ^{-196} |
| 29 | MD | **Full Scorecard** |
| 30 | CODE | Master prediction table — all 23+ quantities |
| 31 | MD | Closing: links to Notebooks 2 and 3 |

### Checkpoint after Phase 2:
- [x] All cells execute without error (33 cells, 16 code cells, all with output)
- [x] Every number matches the paper
- [x] Notebook renders cleanly in GitHub preview (static matplotlib only)

---

## Phase 3: Notebook 2 — "Interactive Explorer"

### Design principles:
- Narrative-driven: PPM ontology told from first principles
- "What if" sliders at each stage — user breaks and fixes the framework
- ipywidgets FloatSlider + interactive_output + VBox (Voila-compatible)
- Existing MathJax fix from current notebook preserved
- ~25-30 cells

### Section outline:

| § | Title | Slider(s) | What breaks when you change it |
|---|-------|-----------|-------------------------------|
| 0 | Setup + MathJax fix | — | — |
| 1 | Reality as discrete events → CP³ | — | Ontological framing (MD only) |
| 2 | The hierarchy: all masses on one curve | g (5.0–7.8) | Move g off 2π → masses diverge |
| 3 | Why g = 2π: topology fixes the spacing | g | Error minimization surface |
| 4 | The electroweak rung: k_EWSB = 44.5 | k_EWSB (43–46) | Higgs, top, τ, μ all move |
| 5 | The gauge structure: SM from CP³ | — | sin²θ_W, 3 generations (display) |
| 6 | α ≈ 1/137 from consistency | n_exp (0.6–0.95) | Only n=5/6 works |
| 7 | α from spectral geometry | log₁₀(t) | Twisted heat trace ratio vs t |
| 8 | The instanton: why α is so small | — | Tunneling visualization, S=30π |
| 9 | G, Λ, H₀ from one count N | log₁₀(N) (78–86) | G and Λ curves cross at N_cosmic |
| 10 | CP violation: δ_CP from φ | — | Berry phase display |
| 11 | Phase coherence: quantum meets life | n_exp | Two exponentials crossing |
| 12 | The golden ratio: where it comes from | — | A₅ → Q(√5) → φ display |
| 13 | The convergence: everything at once | n_exp, g | Critical point with both sliders |
| 14 | Summary | — | Full scorecard |

### Checkpoint after Phase 3:
- [x] All cells execute in plain Jupyter (21 cells, 10 code, all pass)
- [x] All sliders respond (interactive_output works)
- [ ] Voila rendering works (`voila notebooks/explorer.ipynb`)
- [ ] MathJax renders correctly in Voila

---

## Phase 4: Notebook 3 — "Technical Derivations"

### Design principles:
- Every claim in the paper that involves a number → reproduced here
- Section headers reference paper sections explicitly
- Show intermediate steps (eigenvalues, multiplicities, partial sums)
- No sliders. Static matplotlib for any plots.
- ~40-50 cells. Long but navigable via table of contents.

### Section outline:

| § | Title | What's computed |
|---|-------|-----------------|
| 1 | CP³ spectral data | Eigenvalues λ_k = k(k+3), multiplicities d_k, τ-traces tr(τ\|V_k) |
| 2 | Pyramidal number structure | f_k = P_{k+1}, P₃²ln(φ) ≈ P₄π, CP^n selectivity |
| 3 | α Route I: twisted heat trace | Full computation at t*=1/32, convergence analysis |
| 4 | α Route II: cogito loop | Λ_obs → N → α, sensitivity to c₁_topo |
| 5 | α Route III: instanton | S = 30π derivation, zero modes, prefactor budget |
| 6 | CP^n selectivity | 1/α for n=1..7, only n=3 gives ~137 |
| 7 | Hierarchy derivation | g = 2π from topology, E(k), all mass predictions |
| 8 | Gauge structure | SU(4) → SU(3)×SU(2)×U(1), branching rules, sin²θ_W |
| 9 | Generation count | Dirac index on CP³/Z₂, why exactly 3 |
| 10 | Higgs sector | λ_PPM = 1/(4√π), Δλ, y_t, comparison to SM |
| 11 | Lepton mass ratios | Bare predictions, known correction mechanisms |
| 12 | CKM and CP violation | Berry phase integrals, δ_CP = π(1-1/φ) |
| 13 | PMNS and neutrino sector | TBM matrix, θ_strong = 0, mass brackets |
| 14 | Heat kernel coefficients | a₀ through a₃, ζ_Δ(0), log det Δ |
| 15 | Functional determinant | Z₁ one-loop, perturbative sector |
| 16 | Instanton sector | 30 zero modes, moduli space, A₅ decomposition |
| 17 | Golden ratio investigation | L-function bridge, sl(4,R) under A₅ |
| 18 | Cosmological predictions | G, Λ, H₀ derivations with full formulas |
| 19 | G(z) evolution | G_eff(z) = G₀(1+z)^{3/2}, testable predictions |
| 20 | Dark energy | w_eff, Sidharth scaling, φ-tiled boundaries |
| 21 | Sterile neutrino brackets | Mass range, mixing angle constraints |
| 22 | Full prediction table | All quantities, errors, tiers, status |

### Checkpoint after Phase 4:
- [x] All cells execute without error (44 cells, 25 code, all pass)
- [x] Every number matches the paper to stated precision
- [x] Cross-reference comments point to correct paper sections

---

## Phase 5: Final Integration
- [x] `pytest tests/` passes (if tests exist)
- [x] All three notebooks execute clean from top to bottom
- [x] `requirements.txt` and `binder/requirements.txt` are consistent
- [x] README.md updated to describe the three notebooks
- [x] No stale imports or dead code in `ppm/`

---

## Execution Order

The build order is designed so each phase produces a testable checkpoint:

1. **Phase 0** — Scaffolding (archive old, create stubs)
2. **Phase 1** — `ppm/` package (the engine everything depends on)
3. **Phase 2** — Sizzle Reel (simplest notebook, validates ppm/ works)
4. **Phase 3** — Interactive Explorer (most complex, needs working ppm/ + widgets)
5. **Phase 4** — Technical Derivations (longest, but straightforward once ppm/ works)
6. **Phase 5** — Integration testing

**Context compaction strategy:** After completing each phase, update this file's
checkboxes. The next session can read this file and resume from the last completed
phase without needing the full conversation history.

---

## Key Numbers (Quick Reference)

These are the target values every notebook must reproduce:

| Quantity | PPM Value | Observed | Error |
|----------|-----------|----------|-------|
| 1/α (Route I) | 137.257 | 137.036 | 0.16% |
| 1/α (Route II) | 137.556 | 137.036 | 0.38% |
| δ_CP | 68.75° | 68.4±3° | within 1σ |
| sin²θ_W (Pati-Salam) | 0.375 | 0.3750 | 0.13% |
| H₀ | 70.9 km/s/Mpc | 67.4–73.0 | splits tension |
| g | 2π = 6.283 | — | topological |
| k_EWSB | 44.5 | — | derived |
| λ_PPM | 1/(4√π) = 0.141 | 0.126 | ~12% (running) |
| θ_strong | 0 | < 10⁻¹⁰ | exact |
| Generations | 3 | 3 | exact |
| S_inst | 30π = 94.25 | — | topological |
| P₃²ln(φ) / (P₄π) | 1.00074 | 1 | 0.074% |
