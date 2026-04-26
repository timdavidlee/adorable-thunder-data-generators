from adorable_thunder.make.field_generators.address import generate_addresses


def test_generate_addresses_returns_correct_length():
    result = generate_addresses(30)
    assert len(result) == 30


def test_generate_addresses_has_expected_columns():
    result = generate_addresses(5)
    assert list(result.columns) == [
        "street_address",
        "city",
        "state_province",
        "country_code",
        "postal_code",
    ]


def test_generate_addresses_street_address_has_number_and_name():
    result = generate_addresses(20)
    for addr in result["street_address"]:
        parts = addr.split(" ", 1)
        assert parts[0].isdigit()
        assert len(parts[1]) > 0


def test_generate_addresses_country_filter_restricts_output():
    result = generate_addresses(30, country_code="US")
    assert (result["country_code"] == "US").all()
