# PPM Framework — Deriving Physical Constants from Z2 → RP3 Topology

The Process-Phenomenology Mapping (PPM) framework derives fundamental physical constants from the topology of a single geometric structure: the projection Z2 → RP3. The hierarchy scaling factor g = 2π, the fine-structure constant α, Newton's constant G, and the cosmological constant Λ all emerge from a coupled constraint system with zero free parameters at the fundamental level.

This repository contains the computational implementation and reproducible notebooks for the PPM manuscript.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/woz5999/ppm-framework/HEAD)

## Installation

```bash
pip install -e .
```

## Quick Start

Run the notebooks in order:

1. `notebooks/01_hierarchy_and_timescales.ipynb` — Energy hierarchy E(k) and actualization timescales
2. `notebooks/02_constraint_solver.ipynb` — 8-equation constraint system deriving fundamental constants
3. `notebooks/03_phase_coherence.ipynb` — Phase matching condition constraining α
4. `notebooks/04_integration_and_criticality.ipynb` — Critical point at k=61 and temporal integration

## Reproducing Manuscript Results

| Notebook | Manuscript Section                | Result                                                                |
| -------- | --------------------------------- | --------------------------------------------------------------------- |
| 01       | Section 3.3, 7.4.3                | Energy hierarchy table, actualization timescales, temporal nesting    |
| 02       | Section 2.4.1, Appendix B.2, 6.10 | Constraint solver output, parameter comparison, Level 2 count         |
| 03       | Section 3.4, Appendix A.3         | Phase coherence → α = 1/137, sensitivity analysis                     |
| 04       | Section 7.1, 7.2, 7.4.3           | Integration measure Φ(k), critical point signatures, specious present |

## Running Tests

```bash
pytest tests/test_all.py -v
```

## Citation

```bibtex
@article{ppm-framework,
  title={Process-Phenomenology Mapping: Deriving Physical Constants from Z2 → RP3 Topology},
  year={2026},
}
```

## License

MIT
