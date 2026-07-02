"""Record the agent-loop demo as an animated GIF, using only Python + Pillow.

No system tools to install (no vhs, no brew, no ffmpeg). Just:

    pip install pillow
    python demo/record_demo.py            # uses a built-in sample transcript
    python demo/record_demo.py --live     # runs the REAL agent (needs your .env)

Output: demo/agent-demo.gif

Why two modes?
- Default (sample): renders a fixed, representative transcript. Works with zero
  credentials, so anyone can regenerate the GIF for the README.
- --live: actually runs demo_agent.py and records its real output. Use this
  once your AI Service Router keys are set up.
"""

import io
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "agent-demo.gif"

# --- Look of the "terminal" -------------------------------------------------
WIDTH, HEIGHT = 900, 350
PAD = 24
LINE_H = 26
FONT_SIZE = 18
BG = (30, 30, 46)          # dark background
DIM = (108, 112, 134)      # prompt symbol / muted
FG = (205, 214, 244)       # normal text
GREEN = (166, 227, 161)
YELLOW = (249, 226, 175)
CYAN = (137, 220, 235)
PINK = (245, 194, 231)

# ANSI color code -> RGB, so we can reuse the same colors demo_agent.py prints.
ANSI = {"1": FG, "33": YELLOW, "36": CYAN, "32": GREEN, "1;32": GREEN}
_ANSI_RE = re.compile(r"\033\[([0-9;]*)m")

# The monospace font has no color-emoji glyphs, so emojis would render as empty
# boxes. demo_agent.py prints emojis (they look great in a real terminal), so
# for the GIF we swap them for clean ASCII markers before drawing.
_EMOJI = {"🧑 ": "", "🧑": "", "🔧": "*", "↩️  ": "-> ", "↩️ ": "-> ",
          "↩️": "->", "🤖 ": "", "🤖": "", "☀️": "", "✅ ": "", "✅": ""}


def _clean(text: str) -> str:
    for emoji, ascii_ in _EMOJI.items():
        text = text.replace(emoji, ascii_)
    return text


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in (
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/Library/Fonts/Courier New.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
        "C:/Windows/Fonts/consola.ttf",                          # Windows
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()  # last resort, still works


FONT = _load_font(FONT_SIZE)


def _parse_ansi(text: str):
    """Turn a string with ANSI color codes into [(color, text), ...] spans."""
    spans, color, idx = [], FG, 0
    for match in _ANSI_RE.finditer(text):
        if match.start() > idx:
            spans.append((color, text[idx:match.start()]))
        code = match.group(1)
        color = ANSI.get(code, FG) if code and code != "0" else FG
        idx = match.end()
    if idx < len(text):
        spans.append((color, text[idx:]))
    return spans


def _render(lines: list[str]) -> Image.Image:
    """Draw a list of (already colored) terminal lines to one frame."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    # Three little window dots, for that terminal feel.
    for i, dot in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        draw.ellipse((PAD + i * 22, 14, PAD + i * 22 + 12, 26), fill=dot)

    y = PAD + 24
    for line in lines[-12:]:  # keep the last N lines visible
        x = PAD
        for color, chunk in _parse_ansi(_clean(line)):
            draw.text((x, y), chunk, font=FONT, fill=color)
            x += draw.textlength(chunk, font=FONT)
        y += LINE_H
    return img


# A representative transcript. The tool call + tool results are exactly what
# the real tools return (get_weather is deterministic; 17.5% of 2840 = 497.0).
SAMPLE = [
    ("\033[1m$ python demo/demo_agent.py\033[0m", 8),
    ("", 3),
    ("\033[1mYou:\033[0m  What's the weather in Rotterdam, and what is 17.5% of 2840?", 12),
    ("", 3),
    ("  \033[33m* calling get_weather({'city': 'Rotterdam'})\033[0m", 12),
    ("      \033[36m-> Weather in Rotterdam: sunny, 16°C, wind force 4.\033[0m", 12),
    ("  \033[33m* calling calculator({'expression': '17.5/100*2840'})\033[0m", 12),
    ("      \033[36m-> 17.5/100*2840 = 497.0\033[0m", 12),
    ("", 3),
    ("\033[1;32mAgent:\033[0m  It's sunny and 16°C in Rotterdam right now, and", 10),
    ("        17.5% of 2840 is 497. Have a lovely day!", 24),
]


def get_transcript() -> list[tuple[str, int]]:
    """Return [(line, hold_frames), ...]. Live mode captures the real run."""
    if "--live" not in sys.argv:
        return SAMPLE

    # --live: run the real agent and capture what it prints.
    sys.path.insert(0, str(HERE.parent))
    import contextlib

    from demo import demo_agent  # noqa: E402

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        demo_agent.main()
    return [(line, 12) for line in buffer.getvalue().splitlines()]


def main() -> None:
    transcript = get_transcript()
    frames, shown = [], []
    # Build the animation line by line: each new line appears, then holds.
    for line, hold in transcript:
        shown.append(line)
        frame = _render(shown)
        frames.append((frame, 90))                 # ~90ms as the line appears
        frames.append((frame, hold * 100))         # then hold a bit
    # Hold the final frame longer so viewers can read the answer.
    frames.append((_render(shown), 2500))

    images = [f for f, _ in frames]
    durations = [d for _, d in frames]
    images[0].save(
        OUT,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUT}  ({len(images)} frames)")


if __name__ == "__main__":
    main()
