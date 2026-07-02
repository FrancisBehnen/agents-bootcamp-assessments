---
name: comparing-products
description: How to compare two or more products in a clear, structured way
---

# Skill: Comparing products

Use this skill whenever a customer asks about the difference between
products, or which of several options to choose.

## Steps

1. **Fetch the details of every product involved** with get_product_details.
   Compare real specs, never memory.
2. **Compare only what differs AND matters.** Skip specs that are identical
   or irrelevant to the customer's use case.
3. **Present as a compact markdown table**: one row per spec that differs,
   one column per product. Maximum 5 rows, so pick the 5 most decision-relevant
   differences.
4. **Translate the winner per row.** Below the table, one short bullet per
   product: "Choose the X if you ...".
5. **End with a question or a verdict.** If you know the customer's
   situation, give a clear verdict. If not, ask the one question that would
   decide it.

## Example output shape

| | Pixelphone 15 | Pixelphone 15 Ultra |
|---|---|---|
| Price | €799 | €1199 |
| Camera | 50 MP | 200 MP |

- Choose the **15** if you want great value and a compact phone.
- Choose the **15 Ultra** if photography is your hobby.
