"""Shared low-level portfolio-optimization math helpers."""

from __future__ import annotations

import numpy as np

PSEUDOINVERSE_COND_THRESHOLD = 1e12


def add_diagonal_ridge(covariance: np.ndarray, ridge: float) -> np.ndarray:
    """Return a covariance matrix with an optional diagonal ridge added."""

    matrix = np.asarray(covariance, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Covariance must be a square matrix.")
    if ridge < 0.0:
        raise ValueError("Covariance ridge must be non-negative.")
    if np.isclose(ridge, 0.0):
        return matrix.copy()
    return matrix + np.eye(matrix.shape[0], dtype=float) * ridge


def solve_markowitz_system(
    covariance: np.ndarray,
    rhs: np.ndarray,
    *,
    condition_threshold: float = PSEUDOINVERSE_COND_THRESHOLD,
) -> tuple[np.ndarray, str]:
    """Solve one Markowitz linear system with a pseudoinverse fallback."""

    matrix = np.asarray(covariance, dtype=float)
    vector = np.asarray(rhs, dtype=float)
    condition_number = np.linalg.cond(matrix)
    if not np.isfinite(condition_number) or condition_number > condition_threshold:
        solution = np.linalg.pinv(matrix) @ vector
        return solution, "pseudoinverse"
    try:
        solution = np.linalg.solve(matrix, vector)
        return solution, "solve"
    except np.linalg.LinAlgError:
        solution = np.linalg.pinv(matrix) @ vector
        return solution, "pseudoinverse"


def equal_weight_vector(n_assets: int) -> np.ndarray:
    """Return the equal-weight vector."""

    if n_assets < 1:
        raise ValueError("At least one asset is required to build equal weights.")
    return np.full(n_assets, 1.0 / n_assets, dtype=float)


def minimum_variance_weights(
    covariance: np.ndarray,
    *,
    condition_threshold: float = PSEUDOINVERSE_COND_THRESHOLD,
) -> tuple[np.ndarray, str]:
    """Return the fully invested minimum-variance weights."""

    ones = np.ones(np.asarray(covariance).shape[0], dtype=float)
    numerator, method = solve_markowitz_system(
        covariance,
        ones,
        condition_threshold=condition_threshold,
    )
    denominator = float(ones @ numerator)
    if np.isclose(denominator, 0.0):
        raise ValueError("Minimum-variance denominator is zero.")
    return numerator / denominator, method


def tangency_weights(
    mean_returns: np.ndarray,
    covariance: np.ndarray,
    risk_free_rate: float,
    *,
    condition_threshold: float = PSEUDOINVERSE_COND_THRESHOLD,
) -> tuple[np.ndarray, str]:
    """Return the fully invested tangency weights."""

    mean_vector = np.asarray(mean_returns, dtype=float)
    ones = np.ones_like(mean_vector, dtype=float)
    excess_mean = mean_vector - float(risk_free_rate) * ones
    numerator, method = solve_markowitz_system(
        covariance,
        excess_mean,
        condition_threshold=condition_threshold,
    )
    denominator = float(ones @ numerator)
    if np.isclose(denominator, 0.0):
        raise ValueError("Tangency denominator is zero.")
    return numerator / denominator, method
