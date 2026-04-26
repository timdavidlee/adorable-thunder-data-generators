from adorable_thunder.make.field_generators.users import generate_user_emails


def test_generate_user_emails_returns_correct_length():
    result = generate_user_emails(20)
    assert len(result) == 20


def test_generate_user_emails_are_valid_format():
    result = generate_user_emails(20)
    assert all("@" in email for email in result)
