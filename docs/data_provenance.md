# Data provenance

Source: [UCI Default of Credit Card Clients (dataset 350)](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients).

Run `python -m src.fhe_credit.download_data` from the repository root.
The command creates `data/raw/features.csv`, `data/raw/target.csv`, and `data/raw/manifest.json`.
The manifest records the retrieval timestamp, columns, and SHA-256 checksums.
These raw files are ignored by Git. Save the manifest with each experiment or in an approved artifact store when exact reproducibility is required.
The package requirements are ranges, not a frozen lockfile. Record Python and package versions in experiment reports and freeze a lockfile after the environment smoke test.
This dataset concerns existing cardholders and cannot establish the causal effect of underwriting policies for new applicants.
