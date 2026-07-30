# Demo GIF

This folder makes the animated demo shown in the main [README](../README.md):
a short recording of the agent loop (think, call a tool, answer).

## Files

| File | What it is |
|---|---|
| `demo_agent.py` | A finished, working agent (weather + calculator). No TODOs, it just runs. |
| `record_demo.py` | Renders the run to a GIF using only Python + Pillow. No `vhs`, no `brew`, no `ffmpeg`. |
| `agent-demo.gif` | The generated recording, shown in the main README. |
| `scenario_13_demo.py` | Runs mystery-shopper scenario 13 through the Ultimate Agent supervisor. |
| `record_scenario_13_demo.py` | Renders the scenario 13 supervisor flow as a separate GIF. |
| `scenario-13-agent-demo.gif` | Animated scenario 13 demo with order desk, advisor, and tone skill calls. |

## Regenerate the GIF

The GIF is already committed, so you only need this if you want to change it.
Pillow (the only requirement) is already installed by the standard setup
(`pip install -e .`), so there is nothing extra to install:

```bash
python demo/record_demo.py
```

That writes `demo/agent-demo.gif`. It uses a built-in sample transcript, so it
needs no API keys: anyone can regenerate it.

Generate the separate scenario 13 demo with:

```bash
python demo/record_scenario_13_demo.py
```

Want the GIF to capture a **real** agent run instead of the sample?

```bash
python demo/record_demo.py --live     # runs the real agent, needs your .env
```

## Just want to watch it run live in your own terminal?

```bash
python demo/demo_agent.py
```

That one needs your AI Service Router keys set up (`python check_setup.py` to
verify). In a real terminal the emojis show in full color; the GIF uses plain
ASCII markers because the recorder's font has no emoji glyphs.

## Why a demo GIF?

A short GIF shows what the project does in seconds and catches the reader's
eye, which is exactly why good READMEs include one. Building it from the real
agent also doubles as a tiny smoke test that the harness works end to end.
