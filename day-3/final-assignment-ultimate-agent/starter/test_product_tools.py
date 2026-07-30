from harness.data import PRODUCTS
from harness.tools import compare_replacement_products


def compare(source_product: str) -> str:
    return compare_replacement_products.invoke({"source_product": source_product})


def test_known_product_returns_only_other_products_from_same_category():
    result = compare("P-4001")

    assert "P-4001" not in result
    assert "P-4002" in result
    assert "washing machines" in result


def test_known_product_ranks_similarity_before_availability():
    result = compare("P-4001")

    assert result.index("P-4007") < result.index("P-4003")
    assert "P-4007" in result and "OUT OF STOCK" in result


def test_external_product_specs_rank_the_closest_available_match_first():
    result = compare("AEG washing machine, 8 kg, energy label A")

    assert result.index("P-4001") < result.index("P-4002")
    assert "matching specs: capacity, energy_label" in result
    assert "P-4002" in result and "OUT OF STOCK" in result


def test_unknown_category_returns_no_product_candidates():
    result = compare("unknown kitchen appliance")

    assert "Could not determine the source product category" in result
    assert all(product["id"] not in result for product in PRODUCTS)