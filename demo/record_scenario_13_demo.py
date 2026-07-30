"""Render the scenario 13 supervisor demo as an animated GIF.

Run it from the repository root:
    python demo/record_scenario_13_demo.py
"""

from pathlib import Path

from record_demo import _render

OUT = Path(__file__).resolve().with_name("scenario-13-agent-demo.gif")

SAMPLE = [
    ("\033[1mLANGSMITH TRACE - SCENARIO 13\033[0m", 6),
    ("\033[1mCustomer:\033[0m I recently had a problem with my washing machine", 12),
    ("          from order ORD-1006. I want a similar washing machine.", 12),
    ("          Can you recommend one for me?", 14),
    ("", 2),
    ("\033[33mSupervisor [LLM]\033[0m route request and load memory", 5),
    ("  \033[33m* read_notes({})\033[0m", 5),
    ("    \033[36m-> no relevant saved preference\033[0m", 5),
    ("\033[33mSupervisor [LLM]\033[0m identify the exact order item", 5),
    ("  \033[33m* ask_order_desk(order='ORD-1006')\033[0m", 5),
    ("    \033[33mOrder desk [LLM]\033[0m verify order before answering", 5),
    ("      \033[33m* get_order_status(order_id='ORD-1006')\033[0m", 6),
    ("        \033[36m-> delivered item: AquaCare EcoWash 900\033[0m", 6),
    ("    \033[33mOrder desk [LLM]\033[0m return verified item brief", 5),
    ("  \033[36m-> source product: AquaCare EcoWash 900\033[0m", 6),
    ("\033[33mSupervisor [LLM]\033[0m delegate replacement search", 5),
    ("  \033[33m* ask_advisor(product='AquaCare EcoWash 900')\033[0m", 5),
    ("    \033[33mProduct advisor [LLM]\033[0m locate source product", 5),
    ("      \033[33m* search_products(query='AquaCare EcoWash 900')\033[0m", 5),
    ("        \033[36m-> P-4003 AquaCare EcoWash 900\033[0m", 5),
    ("      \033[33m* get_product_details(product_id='P-4003')\033[0m", 5),
    ("        \033[36m-> 9 kg, A label, 47 dB, 1400 rpm\033[0m", 6),
    ("    \033[33mProduct advisor [LLM]\033[0m compare same-category options", 5),
    ("      \033[33m* compare_replacement_products(source='P-4003')\033[0m", 6),
    ("        \033[36m-> returns all washing-machine candidates\033[0m", 5),
    ("    \033[33mProduct advisor [LLM]\033[0m verify best available match", 5),
    ("      \033[33m* get_product_details(product_id='P-4001')\033[0m", 5),
    ("        \033[36m-> FreshSpin 8000: EUR 649, in stock\033[0m", 6),
    ("    \033[33mProduct advisor [LLM]\033[0m return grounded comparison", 5),
    ("  \033[36m-> closest available match: FreshSpin 8000\033[0m", 6),
    ("\033[33mSupervisor [LLM]\033[0m prepare customer response", 5),
    ("  \033[33m* read_skill(name='cool-tone-of-voice')\033[0m", 5),
    ("    \033[36m-> confident, direct, situation-specific style\033[0m", 5),
    ("\033[33mSupervisor [LLM]\033[0m compose final answer", 5),
    ("", 2),
    ("\033[1;32mCoolShop:\033[0m Strong match: the FreshSpin 8000 Washing Machine.", 14),
    ("          It has the same A energy label and 1400 rpm, with an", 12),
    ("          8 kg drum instead of 9 kg. Noise is almost identical:", 12),
    ("          48 dB versus 47 dB. It costs EUR 649 and is in stock.", 18),
]

APPEAR_MS = 360
HOLD_UNIT_MS = 250
FINAL_HOLD_MS = 8000


def _render_trace(lines: list[str]):
    """Render eleven rows so the shared terminal canvas never clips the last one."""
    return _render(lines[-11:])


def main() -> None:
    frames: list[tuple[object, int]] = []
    shown: list[str] = []

    for line, hold in SAMPLE:
        shown.append(line)
        frame = _render_trace(shown)
        frames.append((frame, APPEAR_MS))
        frames.append((frame, hold * HOLD_UNIT_MS))

    frames.append((_render_trace(shown), FINAL_HOLD_MS))
    images = [frame for frame, _ in frames]
    durations = [duration for _, duration in frames]
    images[0].save(
        OUT,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUT} ({len(images)} frames)")


if __name__ == "__main__":
    main()