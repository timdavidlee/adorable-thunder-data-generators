from adorable_thunder.make.field_generators.company import (
    generate_company_and_products,
    generate_company_names,
)


def test_generate_company_names_returns_correct_length():
    result = generate_company_names(30)
    assert len(result) == 30


def test_generate_company_names_are_strings():
    result = generate_company_names(10)
    assert all(isinstance(n, str) for n in result)


def test_generate_company_and_products_returns_correct_shape():
    result = generate_company_and_products(15)
    assert result.shape == (15, 2)


def test_generate_company_and_products_company_name_prefix_in_product():
    result = generate_company_and_products(20)
    for row in result:
        company, product = row
        company_first_word = company.split()[0]
        assert company_first_word in product
