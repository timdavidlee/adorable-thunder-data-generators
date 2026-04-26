from adorable_thunder.make.reference_data.ledger_accounts import ASSET_ACCOUNTS

from adorable_thunder.make.field_generators.ledger_account import generate_ledger_accounts

_ASSET_CODES = {a[0] for a in ASSET_ACCOUNTS}


def test_generate_ledger_accounts_returns_correct_length():
    result = generate_ledger_accounts(20)
    assert len(result) == 20


def test_generate_ledger_accounts_has_expected_columns():
    result = generate_ledger_accounts(5)
    assert list(result.columns) == ["account_code", "account_name"]


def test_generate_ledger_accounts_type_filter_restricts_output():
    result = generate_ledger_accounts(30, account_type="asset")
    assert all(code in _ASSET_CODES for code in result["account_code"])
