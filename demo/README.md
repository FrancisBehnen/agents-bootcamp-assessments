# Demo GIF

This folder generates the animated demo shown in the main [README](../README.md):
a short terminal recording of the agent loop (think, call a tool, answer).

## Files

| File | What it is |
|---|---|
| `demo_agent.py` | A finished, working agent (weather + calculator). No TODOs, it just runs. |
| `agent-demo.tape` | A [vhs](https://github.com/charmbracelet/vhs) script that records the run as a GIF. |
| `agent-demo.gif` | The generated recording (created by the command below). |

## How to (re)generate the GIF

1. Install **vhs** (a terminal-to-GIF recorder):

   ```bash
   brew install vhs          # macOS
   # or see https://github.com/charmbracelet/vhs for other systems
   ```

2. Make sure your `.env` is filled in and the setup passes:

   ```bash
   python check_setup.py
   ```

3. From the **repo root**, record the GIF:

   ```bash
   vhs demo/agent-demo.tape
   ```

   This runs `demo_agent.py`, captures the terminal, and writes
   `demo/agent-demo.gif`.

4. Show it in the main README by adding this line under a "See it in action"
   heading:

   ```markdown
   ![Agent demo](demo/agent-demo.gif)
   ```

## Why a demo GIF?

A short GIF shows what the project does in seconds and catches the reader's
eye, which is exactly why good READMEs include one. Recording it from a real
run (instead of a mock-up) also doubles as a quick smoke test that the harness
and your router credentials actually work end to end.
