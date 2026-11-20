import numpy as np
from src.fhe_credit.policies import cutoff, capacity, expected_utility, disagreement


def test_cutoff():
    assert cutoff([0.1, 0.2, 0.3], 0.2).tolist() == [True, True, False]


def test_capacity():
    assert capacity([0.3, 0.1, 0.2, 0.4], 0.5).tolist() == [False, True, True, False]


def test_utility():
    assert expected_utility([0.0, 1.0], [100, 100]).tolist() == [12.0, -80.0]


def test_disagreement():
    assert np.isclose(disagreement([1, 0], [1, 1]), 0.5)
