"""Download UCI dataset 350 and record reproducible data provenance."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
from ucimlrepo import fetch_ucirepo

DATASET_ID = 350
SOURCE = "https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients"

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def main():
    dataset = fetch_ucirepo(id=DATASET_ID)
    X, y = dataset.data.features, dataset.data.targets
    out = Path("data/raw")
    out.mkdir(parents=True, exist_ok=True)
    features = out / "features.csv"
    target = out / "target.csv"
    X.to_csv(features, index=False)
    y.to_csv(target, index=False)
    manifest = {
        "dataset_id": DATASET_ID,
        "source": SOURCE,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": len(X),
        "features": list(X.columns),
        "target_columns": list(y.columns),
        "files_sha256": {"features.csv": sha256(features), "target.csv": sha256(target)},
        "note": "Hashes identify this download; upstream UCI data may change over time.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Downloaded {len(X)} rows, {X.shape[1]} features; target={list(y.columns)}")
    print("Provenance saved to data/raw/manifest.json")

if __name__ == "__main__":
    main()
