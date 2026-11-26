from src.fhe_credit.dataset_audit.runner import slug


def test_slug_normalizes_official_freddie_name():
    assert slug("Original Loan-to-Value (LTV)") == "original_loan_to_value_ltv"
