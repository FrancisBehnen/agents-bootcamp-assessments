"""Skill tools: list_skills and read_skill.

A *skill* is a plain markdown file with step-by-step instructions for one
specific task, like an instruction card you hand a new colleague. The trick
is that the agent only loads a skill when it needs it:

  1. list_skills()      → shows just the names + one-line descriptions (cheap)
  2. read_skill("...")  → loads the full instructions for ONE skill

This is called "progressive disclosure": don't stuff everything into the
system prompt, let the agent pull in context on demand. It keeps the context
window clean AND lets non-programmers improve the agent by editing markdown.

Skills are read from a `skills/` folder in the directory you run your agent
from (day-2/assignment-2-skills-agent has one ready to go).
"""

from pathlib import Path

from langchain.tools import tool

# Relative path: resolved against the folder you run your script from.
_SKILLS_DIR = Path("skills")


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Read the name/description header between the '---' lines of a skill file."""
    meta = {}
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
    return meta


@tool
def list_skills() -> str:
    """List the available skills (name + short description).

    Call this first to discover what specialised instructions exist.
    Then use read_skill(name) to load the one you need.
    """
    if not _SKILLS_DIR.is_dir():
        return (
            "No skills/ folder found. (Are you running from the right directory? "
            "The skills folder must sit next to your script.)"
        )
    entries = []
    for path in sorted(_SKILLS_DIR.glob("*.md")):
        meta = _parse_frontmatter(path.read_text())
        name = meta.get("name", path.stem)
        description = meta.get("description", "(no description)")
        entries.append(f"- {name}: {description}")
    if not entries:
        return "The skills/ folder exists but contains no .md skill files."
    return "Available skills:\n" + "\n".join(entries)


@tool
def read_skill(name: str) -> str:
    """Read the full instructions of one skill. Follow them precisely.

    Args:
        name: The skill name exactly as shown by list_skills, e.g. "writing-product-advice".
    """
    if not _SKILLS_DIR.is_dir():
        return "No skills/ folder found."
    for path in sorted(_SKILLS_DIR.glob("*.md")):
        meta = _parse_frontmatter(path.read_text())
        if meta.get("name", path.stem) == name.strip():
            return path.read_text()
    return f"No skill named '{name}'. Use list_skills to see what's available."
