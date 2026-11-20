"""Smoke test: run on a supported Concrete ML environment after installation."""
import numpy as np
from concrete.ml.sklearn import DecisionTreeClassifier

rng = np.random.default_rng(42)
X = rng.integers(0, 8, size=(100, 2)).astype(np.float32)
y = (X[:, 0] + X[:, 1] > 7).astype(int)
model = DecisionTreeClassifier(n_bits=3, max_depth=2, random_state=42)
model.fit(X, y)
model.compile(X)
sample = X[:1]
clear = model.predict(sample, fhe='disable')
encrypted = model.predict(sample, fhe='execute')
print('clear:', clear, 'FHE:', encrypted, 'equal:', np.array_equal(clear, encrypted))
