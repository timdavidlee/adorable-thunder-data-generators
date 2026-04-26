from adorable_thunder.make.field_generators.carrier import generate_carriers


def test_generate_carriers_returns_correct_length():
    result = generate_carriers(20)
    assert len(result) == 20


def test_generate_carriers_has_expected_columns():
    result = generate_carriers(5)
    assert list(result.columns) == ["carrier_scac", "carrier_name", "transport_mode"]


def test_generate_carriers_mode_filter_restricts_output():
    result = generate_carriers(30, mode="ocean")
    assert (result["transport_mode"] == "ocean").all()


def test_generate_carriers_invalid_mode_falls_back_to_all():
    result = generate_carriers(20, mode="not_a_real_mode")
    assert len(result) == 20
