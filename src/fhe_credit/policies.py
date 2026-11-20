"""Offline experimental policies; not production underwriting."""
import numpy as np


def cutoff(scores, threshold):
    return np.asarray(scores) <= threshold


def capacity(scores, fraction):
    """Exactly floor(fraction * n) approvals; ties broken by row index."""
    s = np.asarray(scores)
    if not 0 <= fraction <= 1:
        raise ValueError('fraction must be between 0 and 1')
    chosen = np.argsort(s, kind='stable')[:int(np.floor(fraction * len(s)))]
    mask = np.zeros(len(s), dtype=bool)
    mask[chosen] = True
    return mask


def expected_utility(scores, exposure, revenue_rate=0.12, lgd=0.8, cost=0.0):
    """Illustrative one-period utility; rates/units must be justified in study."""
    p = np.asarray(scores)
    e = np.asarray(exposure)
    return e * ((1-p) * revenue_rate - p * lgd) - cost


def disagreement(a, b):
    return float(np.mean(np.asarray(a) != np.asarray(b)))
