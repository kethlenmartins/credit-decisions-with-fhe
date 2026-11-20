"""First baseline; intentionally no FHE yet. Thresholds are not tuned on test."""
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from src.fhe_credit.policies import cutoff


def main():
    root = Path('data/raw')
    X = pd.read_csv(root / 'features.csv')
    y = pd.read_csv(root / 'target.csv').iloc[:, 0].astype(int)
    # Dataset 350 includes a pre-existing credit limit and repayment history;
    # it does NOT represent initial application underwriting.
    X = X.select_dtypes(include='number').drop(columns=['ID'], errors='ignore')
    X_train, X_hold, y_train, y_hold = train_test_split(X, y, test_size=0.4, stratify=y, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_hold, y_hold, test_size=0.5, stratify=y_hold, random_state=42)
    model = DecisionTreeClassifier(max_depth=3, min_samples_leaf=100, random_state=42)
    model.fit(X_train, y_train)
    scores = model.predict_proba(X_test)[:, 1]
    print({'n_train': len(X_train), 'n_val': len(X_val), 'n_test': len(X_test),
           'auc': round(roc_auc_score(y_test, scores), 4),
           'average_precision': round(average_precision_score(y_test, scores), 4),
           'brier': round(brier_score_loss(y_test, scores), 4),
           'approval_rate_at_0.2': round(float(cutoff(scores, 0.2).mean()), 4)})


if __name__ == '__main__':
    main()
