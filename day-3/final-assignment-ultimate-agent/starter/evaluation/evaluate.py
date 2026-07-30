"""Offline evaluation runner for the CoolShop supervisor system.

Loads the evaluation dataset, replays every case against the real supervisor in
its own fresh conversation thread, runs both evaluators from `evaluators.py`,
and prints a per-case report plus an aggregate scorecard.

Run it from anywhere:
    cd day-3/final-assignment-ultimate-agent/starter/evaluation
    python evaluate.py                        # full dataset
    python evaluate.py --case L3-09 L4-13     # only matching case ids
    python evaluate.py --no-judge             # evaluator 1 only, no model calls
    python evaluate.py --out scorecard.json   # also save machine-readable results

See README.md for what the numbers mean.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import uuid4

from harness.tools import memory as memory_tools

from evaluators import (
    OUTCOME_LABELS,
    AnswerOutcome,
    ToolCallCollector,
    build_judge,
    evaluate_tool_use,
    extract_final_answer,
    judge_answer_outcome,
)

EVAL_DIR = Path(__file__).resolve().parent
STARTER_DIR = EVAL_DIR.parent
DEFAULT_DATASET = EVAL_DIR / "eval_cases.json"
# The evaluation gets its own long-term memory file, so a run neither depends on
# nor pollutes the notes from your manual chats in .agent_memory.json.
EVAL_MEMORY_FILE = EVAL_DIR / ".eval_agent_memory.json"


def load_supervisor():
    """Import the agent system from main.py without running its CLI loop.

    Runs from the starter folder whatever directory the runner was started in, so
    an evaluated turn behaves exactly like `python main.py`. Harness state such as
    the memory tools' `.agent_memory.json` is resolved against the working
    directory, and a mismatch there means evaluating an agent you do not ship.
    (`skills/` used to be cwd-relative too; main.py now pins it explicitly with
    configure_skills_directory.)
    """
    os.chdir(STARTER_DIR)
    main_file = STARTER_DIR / "main.py"
    spec = importlib.util.spec_from_file_location("ultimate_agent_main", main_file)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load the agent from {main_file}")
    main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main)
    return main.supervisor


def load_cases(dataset: Path, wanted: list[str] | None = None) -> list[dict[str, Any]]:
    """Load dataset cases, optionally filtered by case-id substring."""
    payload = json.loads(dataset.read_text())
    cases = payload["cases"] if isinstance(payload, dict) else payload
    if wanted:
        needles = [needle.lower() for needle in wanted]
        cases = [
            case
            for case in cases
            if any(needle in case["case_id"].lower() for needle in needles)
        ]
    return cases


def reset_long_term_memory(notes: list[str]) -> None:
    """Point the memory tools at the eval memory file and seed it for one case."""
    memory_tools._MEMORY_FILE = EVAL_MEMORY_FILE
    EVAL_MEMORY_FILE.write_text(json.dumps(notes, indent=2))


def run_case(supervisor, case: dict[str, Any]) -> dict[str, Any]:
    """Replay one case in a fresh thread and evaluate the final turn."""
    case_id = case["case_id"]
    question = case["customer_question"]
    reset_long_term_memory(case.get("long_term_notes", []))
    config: dict[str, Any] = {
        "configurable": {"thread_id": f"eval-{case_id}-{uuid4()}"},
        "tags": ["evaluation-target", case_id],
        "metadata": {"eval_case_id": case_id},
    }

    # Setup turns build conversation context but are not evaluated themselves.
    setup_answers: list[str] = []
    for turn in case.get("setup_turns", []):
        result = supervisor.invoke({"messages": [{"role": "user", "content": turn}]}, config)
        setup_answers.append(extract_final_answer(result["messages"]))

    collector = ToolCallCollector()
    result = supervisor.invoke(
        {"messages": [{"role": "user", "content": question}]},
        {**config, "callbacks": [collector]},
    )
    messages = result["messages"]
    # The checkpointer returns the whole thread; only score the evaluated turn.
    turn_messages = messages[_last_human_index(messages) :]

    tool_use = evaluate_tool_use(
        turn_messages,
        collected_tool_names=collector.tool_names,
        expects_tool_call=case.get("expects_tool_call"),
    )
    return {
        "case_id": case_id,
        "customer_question": question,
        "setup_answers": setup_answers,
        "final_answer": extract_final_answer(turn_messages),
        "tool_use": asdict(tool_use) | {"meets_expectation": tool_use.meets_expectation},
        "expected_outcome": case.get("expected_outcome"),
        "notes": case.get("notes"),
    }


def _last_human_index(messages: list[Any]) -> int:
    """Index of the last customer message, i.e. the start of the evaluated turn."""
    for index in range(len(messages) - 1, -1, -1):
        if getattr(messages[index], "type", None) == "human":
            return index
    return 0


def add_outcome(record: dict[str, Any], judge: Any | None) -> dict[str, Any]:
    """Attach the LLM judge's outcome label to a case record."""
    if judge is None:
        record["outcome"] = None
        return record
    outcome: AnswerOutcome = judge_answer_outcome(
        record["customer_question"], record["final_answer"], judge=judge
    )
    record["outcome"] = outcome.model_dump()
    expected = record.get("expected_outcome")
    record["outcome_matches_expected"] = (
        None if expected is None else outcome.label == expected
    )
    return record


# ===========================================================================
# Reporting
# ===========================================================================
def _percentage(count: int, total: int) -> str:
    return "n/a" if total == 0 else f"{count / total:.0%}"


def _short(text: str, limit: int = 200) -> str:
    """Shorten an error for the terminal; --out keeps the full text."""
    text = " ".join(text.split())
    return text if len(text) <= limit else f"{text[:limit]}..."


def print_case(record: dict[str, Any]) -> None:
    tool_use = record["tool_use"]
    outcome = record.get("outcome")
    print(f"\n=== {record['case_id']} ===")
    print(f"  Q: {record['customer_question']}")
    if record["final_answer"]:
        print(f"  A: {record['final_answer']}")
    else:
        print("  A: <no customer-facing answer>")
    if record.get("error"):
        print(f"  ERROR: {_short(record['error'])}")
        return
    expectation = tool_use["expects_tool_call"]
    verdict = "PASS" if tool_use["meets_expectation"] else "FAIL"
    if tool_use["meets_expectation"] is None:
        verdict = "not scored"
    print(
        f"  Tool called before answer: {tool_use['tool_called_before_answer']}"
        f" (expected: {expectation}, {verdict})"
    )
    print(f"  Tools called: {' -> '.join(tool_use['tools_called']) or 'none'}")
    if record.get("outcome_error"):
        print(f"  Outcome: not labelled, judge failed: {_short(record['outcome_error'])}")
    elif outcome:
        match = record.get("outcome_matches_expected")
        suffix = "" if match is None else f", expected {record['expected_outcome']}: {'PASS' if match else 'FAIL'}"
        print(f"  Outcome: {outcome['label']} (confidence {outcome['confidence']:.2f}{suffix})")
        print(f"  Judge rationale: {outcome['rationale']}")


def print_scorecard(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Print and return the aggregate scorecard."""
    scored = [record for record in records if not record.get("error")]
    errors = len(records) - len(scored)

    with_tool = [r for r in scored if r["tool_use"]["tool_called_before_answer"]]
    expectation_scored = [r for r in scored if r["tool_use"]["meets_expectation"] is not None]
    expectation_met = [r for r in expectation_scored if r["tool_use"]["meets_expectation"]]

    judged = [r for r in scored if r.get("outcome")]
    label_counts = {
        label: sum(1 for r in judged if r["outcome"]["label"] == label)
        for label in OUTCOME_LABELS
    }
    outcome_scored = [r for r in judged if r.get("outcome_matches_expected") is not None]
    outcome_matched = [r for r in outcome_scored if r["outcome_matches_expected"]]
    judge_failures = [r["case_id"] for r in scored if r.get("outcome_error")]

    print("\n" + "=" * 60)
    print("SCORECARD")
    print("=" * 60)
    print(f"Cases run: {len(records)} ({errors} error(s))")
    print(
        f"Tool called before answer: {len(with_tool)}/{len(scored)}"
        f" ({_percentage(len(with_tool), len(scored))})"
    )
    print(
        f"Matches tool expectation:  {len(expectation_met)}/{len(expectation_scored)}"
        f" ({_percentage(len(expectation_met), len(expectation_scored))})"
    )
    if judged:
        print(f"Outcome labels ({len(judged)} judged):")
        for label, count in label_counts.items():
            print(f"  {label:<30} {count:>2} ({_percentage(count, len(judged))})")
        print(
            f"Matches expected outcome:  {len(outcome_matched)}/{len(outcome_scored)}"
            f" ({_percentage(len(outcome_matched), len(outcome_scored))})"
        )
    elif judge_failures:
        print("Outcome labels: none (the judge could not label any case)")
    elif scored:
        print("Outcome labels: none (judge disabled with --no-judge)")
    else:
        print("Outcome labels: none (no case produced an answer to judge)")
    if judge_failures:
        print(f"Judge could not label: {', '.join(judge_failures)}")

    failures = [
        r["case_id"]
        for r in scored
        if r["tool_use"]["meets_expectation"] is False
        or r.get("outcome_matches_expected") is False
    ]
    if failures:
        print(f"Cases needing a look: {', '.join(failures)}")

    return {
        "cases_run": len(records),
        "errors": errors,
        "tool_called_before_answer": {
            "count": len(with_tool),
            "of": len(scored),
            "percentage": _percentage(len(with_tool), len(scored)),
        },
        "matches_tool_expectation": {
            "count": len(expectation_met),
            "of": len(expectation_scored),
            "percentage": _percentage(len(expectation_met), len(expectation_scored)),
        },
        "outcome_labels": label_counts,
        "judge_could_not_label": judge_failures,
        "matches_expected_outcome": {
            "count": len(outcome_matched),
            "of": len(outcome_scored),
            "percentage": _percentage(len(outcome_matched), len(outcome_scored)),
        },
        "cases_needing_a_look": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument(
        "--case",
        nargs="+",
        metavar="ID",
        help="Only run cases whose id contains one of these substrings.",
    )
    parser.add_argument(
        "--no-judge",
        action="store_true",
        help="Skip evaluator 2, so the run makes no judge model calls.",
    )
    parser.add_argument("--out", type=Path, help="Write the full results as JSON.")
    args = parser.parse_args()

    # Resolve paths against the caller's directory, because load_supervisor()
    # changes the working directory to the starter folder.
    dataset = args.dataset.resolve()
    out = args.out.resolve() if args.out else None

    cases = load_cases(dataset, args.case)
    if not cases:
        raise SystemExit("No cases matched. Check --case or the dataset path.")

    supervisor = load_supervisor()
    judge = None if args.no_judge else build_judge()

    print(f"Evaluating {len(cases)} case(s) from {dataset.name}")
    records: list[dict[str, Any]] = []
    for case in cases:
        try:
            record = run_case(supervisor, case)
        except Exception as error:  # one broken case must not sink the run
            record = {
                "case_id": case["case_id"],
                "customer_question": case["customer_question"],
                "final_answer": "",
                "tool_use": {
                    "tool_called_before_answer": False,
                    "tools_called": [],
                    "expects_tool_call": case.get("expects_tool_call"),
                    "meets_expectation": None,
                },
                "error": f"{type(error).__name__}: {error}",
            }
        else:
            # A judge that cannot label an answer is an evaluator failure, not an
            # agent failure. The prompt-injection case hits exactly this: the
            # judge's own prompt quotes the jailbreak and gets content-filtered.
            try:
                record = add_outcome(record, judge)
            except Exception as error:
                record["outcome"] = None
                record["outcome_error"] = f"{type(error).__name__}: {error}"
        records.append(record)
        print_case(record)

    scorecard = print_scorecard(records)
    if out:
        out.write_text(json.dumps({"scorecard": scorecard, "cases": records}, indent=2))
        print(f"\nSaved results to {out}")


if __name__ == "__main__":
    main()
