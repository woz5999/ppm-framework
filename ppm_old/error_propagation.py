"""
PPM Framework — Error Propagation
===================================

Uncertainty quantification for constraint solver outputs via linear
error propagation and Monte Carlo sampling.

Manuscript references: Section 6.10
"""

import numpy as np
from .constraint_solver import constraint_solver, default_initial_guess


def propagate_uncertainty(func,
                           params: np.ndarray,
                           uncertainties: np.ndarray) -> np.ndarray:
    """
    Linear error propagation via finite-difference derivatives.

    Computes sigma_f = sqrt(sum_i (df/dp_i * sigma_i)^2)
    for a scalar function f(params).

    Parameters
    ----------
    func : callable
        Function f(params) -> float.
    params : np.ndarray
        Parameter central values.
    uncertainties : np.ndarray
        Parameter uncertainties (1-sigma).

    Returns
    -------
    np.ndarray
        Propagated uncertainty for each output.
    """
    params = np.asarray(params, dtype=float)
    uncertainties = np.asarray(uncertainties, dtype=float)

    f0 = np.atleast_1d(func(params))
    n_params = len(params)
    n_outputs = len(f0)

    # Jacobian via finite differences
    J = np.zeros((n_outputs, n_params))
    for i in range(n_params):
        h = 1e-8 * max(abs(params[i]), 1.0)
        p_plus = params.copy()
        p_plus[i] += h
        J[:, i] = (np.atleast_1d(func(p_plus)) - f0) / h

    # sigma_f = sqrt(sum (J_ij * sigma_j)^2)
    sigma_f = np.sqrt(np.sum((J * uncertainties[np.newaxis, :]) ** 2, axis=1))
    return sigma_f


def monte_carlo_errors(n_samples: int = 1000,
                       seed: int = 42,
                       verbose: bool = True) -> dict:
    """
    Estimate constraint solver output uncertainties via Monte Carlo.

    Samples input parameter distributions around the physical initial
    guess, solves the constraint system for each sample, and returns
    statistics on the solution distribution.

    Parameters
    ----------
    n_samples : int
        Number of Monte Carlo samples.
    seed : int
        Random seed for reproducibility.
    verbose : bool
        If True, print progress every 100 samples.

    Returns
    -------
    dict
        Keys:
        - 'means' : np.ndarray, shape (8,) — mean of each parameter
        - 'stds' : np.ndarray, shape (8,) — std dev of each parameter
        - 'samples' : np.ndarray, shape (n_converged, 8) — all converged solutions
        - 'convergence_rate' : float — fraction of samples that converged
        - 'parameter_names' : list[str]
    """
    rng = np.random.default_rng(seed)
    x0_base = default_initial_guess()

    # Perturbation scales: ~5% relative for most, ~1% for well-known
    rel_sigma = np.array([
        0.05,    # K
        0.03,    # T
        0.001,   # alpha_EM (very well known)
        0.05,    # alpha_w
        0.05,    # alpha_s
        0.001,   # G (well measured)
        0.10,    # g_G (less constrained)
        0.05,    # Lambda
    ])

    samples = []
    n_converged = 0

    for i in range(n_samples):
        # Perturb initial guess
        perturbation = 1.0 + rel_sigma * rng.standard_normal(8)
        x0_perturbed = x0_base * perturbation

        # Ensure physical bounds
        x0_perturbed[0] = max(x0_perturbed[0], 1.0)    # K > 0
        x0_perturbed[1] = max(x0_perturbed[1], 100.0)   # T > 0
        x0_perturbed[2] = max(x0_perturbed[2], 1e-5)    # alpha > 0
        x0_perturbed[5] = max(x0_perturbed[5], 1e-15)   # G > 0
        x0_perturbed[7] = max(x0_perturbed[7], 1e-60)   # Lambda > 0

        try:
            x, converged, _ = constraint_solver(x0_perturbed, max_iter=50)
            if converged and np.all(np.isfinite(x)):
                samples.append(x)
                n_converged += 1
        except Exception:
            pass

        if verbose and (i + 1) % 100 == 0:
            print(f"  MC sample {i+1}/{n_samples}: {n_converged} converged")

    samples = np.array(samples)

    param_names = ['K', 'T', 'alpha_EM', 'alpha_w', 'alpha_s',
                   'G', 'g_G', 'Lambda']

    result = {
        'means': np.mean(samples, axis=0) if len(samples) > 0 else np.full(8, np.nan),
        'stds': np.std(samples, axis=0) if len(samples) > 0 else np.full(8, np.nan),
        'samples': samples,
        'convergence_rate': n_converged / n_samples,
        'parameter_names': param_names,
    }

    if verbose:
        print(f"\nMonte Carlo complete: {n_converged}/{n_samples} converged "
              f"({result['convergence_rate']*100:.1f}%)")
        if len(samples) > 0:
            print(f"\n{'Parameter':<12} {'Mean':>14} {'± Std':>14}")
            print("-" * 42)
            for name, mean, std in zip(param_names, result['means'], result['stds']):
                print(f"{name:<12} {mean:>14.6e} {std:>14.6e}")

    return result
