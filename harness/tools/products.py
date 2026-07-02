"""Webshop tools: search the catalog and look up product details.

This pair of tools demonstrates a very common pattern:
  1. a broad SEARCH tool that returns short summaries (cheap on context), and
  2. a narrow DETAIL tool that returns everything about one item.

Why split them? Context engineering! If search returned every spec of every
match, the agent's context window would fill up with text it doesn't need.
Let the agent search first, then zoom in. You'll see this same
"progressive disclosure" idea again with skills on day 2.
"""

from langchain.tools import tool

from harness.data import PRODUCTS


@tool
def search_products(query: str) -> str:
    """Search the webshop catalog for products.

    Matches on product name, brand and category. Returns a short summary per
    match (id, name, price, stock). Use get_product_details for full specs.

    Args:
        query: What to search for, e.g. "laptop", "SoundWave" or "washing machine".
    """
    words = query.lower().split()
    matches = []
    for product in PRODUCTS:
        haystack = f"{product['name']} {product['brand']} {product['category']}".lower()
        if any(word in haystack for word in words):
            matches.append(product)

    if not matches:
        return (
            f"No products found for '{query}'. "
            "Try a broader term like 'laptop', 'phone', 'headphones', "
            "'washing machine', 'coffee' or 'monitor'."
        )

    lines = [f"Found {len(matches)} product(s):"]
    for p in matches:
        stock = f"{p['stock']} in stock" if p["stock"] > 0 else "OUT OF STOCK"
        lines.append(
            f"- [{p['id']}] {p['name']} — €{p['price']:.2f} — rating {p['rating']}/5 — {stock}"
        )
    return "\n".join(lines)


@tool
def get_product_details(product_id: str) -> str:
    """Get the full details (specs, price, stock, description) for one product.

    Args:
        product_id: The product id from search results, e.g. "P-1001".
    """
    for p in PRODUCTS:
        if p["id"].lower() == product_id.strip().lower():
            specs = "\n".join(f"  - {key}: {value}" for key, value in p["specs"].items())
            stock = f"{p['stock']} in stock" if p["stock"] > 0 else "OUT OF STOCK"
            return (
                f"{p['name']} ({p['id']})\n"
                f"Brand: {p['brand']} | Category: {p['category']}\n"
                f"Price: €{p['price']:.2f} | {stock} | Rating: {p['rating']}/5\n"
                f"Specs:\n{specs}\n"
                f"In short: {p['highlight']}"
            )
    return f"No product found with id '{product_id}'. Use search_products to find valid ids."
