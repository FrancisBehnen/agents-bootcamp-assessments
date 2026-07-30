from harness.data import PRODUCTS
from harness.tools import compare_replacement_products


def compare(source_product: str) -> str:
    return compare_replacement_products.invoke({"source_product": source_product})


def test_known_product_profile_comes_before_other_products_from_same_category():
    result = compare("P-4001")
    candidates = result.split("Replacement candidates", maxsplit=1)[1]

    assert result.startswith("Source product to replace: [P-4001]")
    assert "P-4001" not in candidates
    assert "P-4002" in candidates
    assert "washing machines" in result


def test_known_product_returns_complete_profiles_for_agent_comparison():
    result = compare("P-4003")

    assert "Brand: AquaCare" in result
    assert "capacity: 9 kg" in result
    assert "[P-4007] AquaCare SilentWash 800" in result
    assert "capacity: 8 kg" in result
    assert "not ranked" in result


def test_external_product_description_and_candidate_specs_are_returned():
    result = compare("AEG washing machine, 8 kg, energy label A")

    assert result.startswith(
        "Source description to replace: AEG washing machine, 8 kg, energy label A"
    )
    assert "[P-4001]" in result and "capacity: 8 kg" in result
    assert "P-4002" in result and "OUT OF STOCK" in result


def test_unknown_category_returns_no_product_candidates():
    result = compare("unknown kitchen appliance")

    assert "Could not determine the source product category" in result
    assert all(product["id"] not in result for product in PRODUCTS)