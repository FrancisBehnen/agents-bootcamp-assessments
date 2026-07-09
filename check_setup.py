"""Setup checker for the Agents Bootcamp.

Run this once after following the setup steps in README.md:

    python check_setup.py

It verifies, in order:
  1. Your .env file exists and the required keys are filled in
  2. The harness package is installed
  3. Your API key actually works (it makes one tiny, cheap LLM call)
  4. LangSmith tracing is switched on

If a step fails, the script tells you how to fix it and stops.
"""

import os
import shutil
import sys
from pathlib import Path

# On Windows this enables ANSI color codes in the terminal, so the checkmarks
# below show in color instead of as raw escape codes.
if os.name == "nt":
    os.system("")

REPO_ROOT = Path(__file__).resolve().parent

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def ok(msg: str) -> None:
    print(f"{GREEN}  ✅ {msg}{RESET}")


def fail(msg: str, fix: str) -> None:
    print(f"{RED}  ❌ {msg}{RESET}")
    print(f"{YELLOW}     Fix: {fix}{RESET}")
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"{YELLOW}  ⚠️  {msg}{RESET}")


print("\nChecking your Agents Bootcamp setup...\n")

# --- Step 1: .env file ------------------------------------------------------
# If .env is missing, create it from the template automatically. That way
# nobody needs a copy command, and it works the same on Windows, macOS and Linux.
env_file = REPO_ROOT / ".env"
example_file = REPO_ROOT / ".env.example"
if not env_file.exists():
    if not example_file.exists():
        fail(
            "No .env or .env.example found.",
            "Make sure you are running this from the repo root folder.",
        )
    shutil.copy(example_file, env_file)
    print(f"{GREEN}  ✅ Created .env from .env.example{RESET}")
    print(
        f"{YELLOW}     Next step: open .env, paste the keys you received from the "
        f"trainers,\n     then run this again (python check_setup.py).{RESET}"
    )
    sys.exit(0)
ok(".env file found")

from dotenv import load_dotenv  # noqa: E402  (import after the file check on purpose)

load_dotenv(env_file)

# The three AI Service Router variables must all be present.
for var, hint in (
    ("AI_SERVICE_ROUTER_API_KEY", "paste the router API key you received from the trainers"),
    ("AI_SERVICE_ROUTER_CLIENT", "set your registered clientName (e.g. agents_bootcamp)"),
    ("AI_SERVICE_ROUTER_BASE_URL", "keep the default TEST URL from .env.example"),
):
    if not os.getenv(var):
        fail(f"{var} is empty in your .env file.", f"Open .env and {hint}.")
ok("AI Service Router variables are set")

# --- Step 2: harness installed ----------------------------------------------
try:
    from harness import get_llm
except ImportError:
    fail(
        "The `harness` package is not installed.",
        "Run `pip install -e .` from the repo root (with your venv activated).",
    )
ok("harness package installed")

# --- Step 3: one tiny LLM call ----------------------------------------------
model_name = os.getenv("BOOTCAMP_MODEL", "gpt-4.1-mini-2025-04-14")
print(f"\n  Making one small test call to {model_name} via the AI Service Router ...")
try:
    llm = get_llm()
    response = llm.invoke("Reply with exactly one word: OK")
except Exception as exc:  # noqa: BLE001 (we want to show any error to the student)
    fail(
        f"The router call failed: {exc}",
        "Common causes: wrong API key, wrong clientName (401 Invalid client), "
        "or you're not on the Coolblue network/VPN. Ask #virtual-agents-platform if stuck.",
    )
ok(f'Router responded: "{response.content}"')

# --- Step 4: LangSmith tracing ----------------------------------------------
tracing = os.getenv("LANGSMITH_TRACING", "").lower() == "true"
api_key = bool(os.getenv("LANGSMITH_API_KEY"))
project = os.getenv("LANGSMITH_PROJECT", "(default)")

if tracing and api_key:
    ok(f'LangSmith tracing is ON, project "{project}"')
    print(
        "\n     Your test call above was traced! Go look at it:\n"
        "     → https://eu.smith.langchain.com  (open your project, click the trace)"
    )
elif tracing and not api_key:
    warn("LANGSMITH_TRACING=true but LANGSMITH_API_KEY is empty, so tracing won't work yet.")
else:
    warn(
        "LangSmith tracing is OFF. You'll want it ON for the bootcamp, so\n"
        "     set LANGSMITH_TRACING=true and LANGSMITH_API_KEY in your .env."
    )

print(f"\n{GREEN}🎉 You're ready for the bootcamp!{RESET}\n")
