"""Render the scenario 13 supervisor demo as an animated GIF.

Run it from the repository root:
    python demo/record_scenario_13_demo.py
"""

from pathlib import Path

from record_demo import _render

OUT = Path(__file__).resolve().with_name("scenario-13-agent-demo.gif")

SAMPLE = [
    ("\033[1m$ python demo/scenario_13_demo.py\033[0m", 8),
    ("", 3),
    ("\033[1mCustomer:\033[0m I had a problem with the washer from ORD-1006.", 10),
    ("          Can you recommend a similar washing machine?", 10),
    ("", 3),
    ("  \033[33m* calling read_notes({})\033[0m", 8),
    ("      \033[36m-> No saved customer preferences.\033[0m", 8),
    ("  \033[33m* calling ask_order_desk({order: 'ORD-1006'})\033[0m", 10),
    ("      \033[36m-> Order item: AquaCare EcoWash 900.\033[0m", 10),
    ("  \033[33m* calling ask_advisor({product: 'AquaCare EcoWash 900'})\033[0m", 10),
    ("      \033[36m-> Closest available match: FreshSpin 8000, EUR 649.\033[0m", 12),
    ("  \033[33m* calling read_skill({name: 'cool-tone-of-voice'})\033[0m", 8),
    ("      \033[36m-> Confident, direct customer response.\033[0m", 8),
    ("", 3),
    ("\033[1;32mCoolShop:\033[0m Strong match: the FreshSpin 8000 keeps the A label", 10),
    ("          and 1400 rpm, with a similar 8 kg capacity. Price: EUR 649.", 24),
]


def main() -> None:
    frames: list[tuple[object, int]] = []
    shown: list[str] = []

    for line, hold in SAMPLE:
        shown.append(line)
        frame = _render(shown)
        frames.append((frame, 90))
        frames.append((frame, hold * 100))

    frames.append((_render(shown), 3000))
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