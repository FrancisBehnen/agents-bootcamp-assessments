"""Order lookup tool for the mock webshop.

In a real company this tool would call an internal API. The agent code would
look IDENTICAL, and only the body of this function would change. That's the
beauty of tools: they're a clean boundary between "LLM decides" and
"systems do".
"""

from langchain.tools import tool

from harness.data import ORDERS


@tool
def get_order_status(order_id: str) -> str:
    """Look up the status and details of a customer order.

    Args:
        order_id: The order number, e.g. "ORD-1002".
    """
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return (
            f"No order found with number '{order_id}'. "
            "Order numbers look like 'ORD-1234'. Please ask the customer to double-check."
        )

    lines = [
        f"Order {order_id.strip().upper()} for {order['customer']}:",
        f"- Items: {', '.join(order['items'])}",
        f"- Status: {order['status']}",
        f"- Ordered on: {order['ordered_on']}",
    ]
    # Not every order has every field, so only show what exists.
    if "delivered_on" in order:
        lines.append(f"- Delivered on: {order['delivered_on']}")
    if "expected_delivery" in order:
        lines.append(f"- Expected delivery: {order['expected_delivery']}")
    lines.append(f"- Note: {order['note']}")
    return "\n".join(lines)
