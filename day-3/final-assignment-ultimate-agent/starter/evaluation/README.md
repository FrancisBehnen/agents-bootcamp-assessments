# Evaluation

The evaluators run **offline around a complete supervisor invocation**. They are
not registered as agent tools and cannot influence a live customer conversation.
Every case is replayed against the real system in its own fresh conversation
thread, so cases cannot contaminate each other.

See [`../architecture.md`](../architecture.md) for the system under test.

```mermaid
flowchart LR
        Cases[(eval_cases.json<br/>customer questions)] --> Runner[evaluate.py<br/>one fresh thread per case]
        Runner -->|invoke| System[Supervisor and specialists]
        System --> Result[Final answer and tool trace]
        Result --> ToolEval[Evaluator 1<br/>tool called before answer?]
        Result --> AnswerEval[Evaluator 2<br/>answer outcome judge]
        JudgeLLM[get_llm<br/>structured output] --> AnswerEval
        ToolEval --> Report[(Per-case results<br/>and aggregate scorecard)]
        AnswerEval --> Report
```

## Files

Everything evaluation-related lives in this folder; `starter/` keeps only the
system under test.

| File | Contents |
| --- | --- |
| `evaluators.py` | The deterministic trace evaluator, the outcome schema, and the LLM judge. |
| `evaluate.py` | The runner: loads the dataset, invokes the supervisor, scores, reports. |
| `eval_cases.json` | The dataset: one case per mystery-shopper scenario. |
| `test_evaluators.py` | Unit tests for the evaluators. No model calls, no network. |

## Running it

```bash
cd day-3/final-assignment-ultimate-agent/starter/evaluation
python evaluate.py                        # the full dataset
python evaluate.py --case L3-09 L4-13     # only cases whose id contains these
python evaluate.py --no-judge             # evaluator 1 only, zero judge model calls
python evaluate.py --out scorecard.json   # also save machine-readable results
```

The runner works from any directory. It resolves `--dataset` and `--out` against
wherever you started it, then switches to the starter folder before loading the
agent, because the harness resolves `skills/` against the working directory. Run
the agent from the wrong folder and `read_skill` quietly returns "No skills/
folder found", which means you are evaluating a different agent than you ship.

A run seeds and uses its own long-term memory file,
`evaluation/.eval_agent_memory.json`, so results never depend on, or pollute, the
notes from your manual chats in `starter/.agent_memory.json`.

## Evaluator 1: tool called before the answer

Deterministic; no LLM involved, so this evaluator cannot hallucinate. It returns:

- `tool_called_before_answer`: `true` when at least one tool invocation starts
  before the final customer-facing assistant message, otherwise `false`.
- `tools_called`: the ordered tool names, such as `ask_order_desk`,
  `get_order_status`, `ask_advisor`, or `compare_replacement_products`.
- `meets_expectation`: whether the observed usage matches the case's
  `expects_tool_call`, or `None` when the case does not express an expectation.

Two sources are combined, each for what it proves:

- **The supervisor's messages** prove the *ordering*. The final answer is the
  last assistant message that has text and no pending tool calls; any assistant
  message before it that requests tools proves a tool ran first. This is why
  `tool_called_before_answer` is derived from the messages only.
- **A `ToolCallCollector` callback** proves *which* tools ran, including nested
  ones. Calls made by specialist agents count as tool calls, and LangChain
  propagates callbacks into nested runs, so the collector sees the
  `get_order_status` call hidden behind `ask_order_desk`. Inspecting the
  supervisor's messages alone would report only `ask_order_desk`; inspecting the
  final text would prove nothing at all.

Nested calls can only happen inside a supervisor tool call that already precedes
the answer, so the messages-derived Boolean stays exact while the callback
enriches the reported trace. Evaluator model calls are never counted: the judge
runs after the invocation, outside the collector, and its runs go to a separate
LangSmith project (see below).

The aggregate metrics are the percentage of cases with
`tool_called_before_answer`, and the percentage of scored cases that match their
expectation. Scoring against `expects_tool_call` rather than rewarding any tool
call matters as soon as the dataset contains messages that should *not* need a
tool: the prompt-injection case sets `expects_tool_call: null` because refusing
it needs no lookup, so it is reported but not scored.

## Evaluator 2: customer-question outcome

An LLM judge with structured output. Its inputs are the original customer
question and the final customer-facing answer. It returns exactly one label, a
rationale, and a confidence:

| Label | Meaning |
| --- | --- |
| `ANSWERED` | The response directly and usefully addresses the customer's question. |
| `NOT_ANSWERED` | The response evades, misunderstands, or leaves the question unresolved without a useful next step. |
| `DIRECTED_TO_CUSTOMER_SERVICE` | Human customer service is presented as the primary next step because the agent cannot complete the request. |

The precedence rule keeps the labels mutually exclusive: choose
`DIRECTED_TO_CUSTOMER_SERVICE` when escalation is the main resolution; otherwise
choose `ANSWERED` when a substantive answer is present, even if customer service
is mentioned as an optional fallback; choose `NOT_ANSWERED` for all remaining
cases. An honest answer that a product or order cannot be found is still
`ANSWERED` when it explains the limitation and gives a relevant next step, and so
is a clear refusal of an impossible request that says what the agent *can* do.

The judge uses the typed `AnswerOutcome` schema (`label`, `rationale`,
`confidence`) through `with_structured_output`, rather than parsing free-form
model text. An empty answer is labelled `NOT_ANSWERED` without a model call.

**What this evaluator does not measure:** factual correctness, grounding, tone,
or policy compliance. A hallucinated order status reads as `ANSWERED`. Catching
that needs a separate grounding evaluator; today the trace and the mystery-shopper
round cover it.

## The dataset

`eval_cases.json` holds one case per scenario in
[`../test_scenarios.md`](../test_scenarios.md).

| Field | Required | Purpose |
| --- | --- | --- |
| `case_id` | yes | Stable id, used for filtering, thread ids, and LangSmith tags. |
| `customer_question` | yes | The message that is evaluated. |
| `setup_turns` | no | Earlier turns in the same thread, sent but not scored. Used by the "same question twice" case. |
| `long_term_notes` | no | Notes seeded into long-term memory before the case, which makes the memory-recall case reproducible. |
| `expects_tool_call` | no | Expectation for evaluator 1. `null` means "not scored". |
| `expected_outcome` | no | Expected judge label. `null` where more than one label is defensible. |
| `notes` | no | What good looks like, so a failing case is interpretable months later. |

Three cases deliberately leave `expected_outcome` as `null`: the delayed
cancellation, the angry customer, and the VAT question. For those, both a
substantive answer and an escalation are defensible, and pinning a single label
would measure our taste rather than the system.

## Reading the scorecard

The runner prints per case: the question, the final answer, the Boolean tool
verdict with its expectation, the ordered tool names, the outcome label with
confidence, and the judge's rationale. It then aggregates:

```text
Cases run: 13 (0 error(s))
Tool called before answer: 11/13 (85%)
Matches tool expectation:  11/12 (92%)
Outcome labels (12 judged):
  ANSWERED                       10 (83%)
  NOT_ANSWERED                    0 (0%)
  DIRECTED_TO_CUSTOMER_SERVICE    2 (17%)
Matches expected outcome:  8/9 (89%)
Judge could not label: L3-10-prompt-injection
Cases needing a look: L2-06-memory-recall, L3-12-repeated-question
```

Interpretation notes:

- `Matches tool expectation` has a smaller denominator than `Cases run`, because
  unscored cases (`expects_tool_call: null`) are excluded rather than counted as
  passes.
- A `NOT_ANSWERED` label is not automatically a bug. Read the rationale first:
  the honest "nothing matches all three criteria" case *should* be `ANSWERED`,
  while a genuine evasion should not.
- `DIRECTED_TO_CUSTOMER_SERVICE` is the metric to watch over time. A rising
  share means the system is escalating work it used to resolve.
- A high tool-call percentage combined with `NOT_ANSWERED` labels points at
  synthesis, not routing: the specialists were consulted, but the supervisor did
  not turn their briefs into an answer.
- One broken case does not sink the run; it is recorded with its error and
  excluded from the scored denominators.
- `Judge could not label` counts evaluator failures, not agent failures. Those
  cases keep their evaluator-1 verdict and are excluded from the label
  percentages, so a blocked judge never inflates or deflates the outcome mix.

## What the evaluation found

The scorecard above is real output, and every deviation in it is a finding rather
than noise. This is the part worth demoing: none of these were visible from
reading prompts or clicking through a happy-path conversation.

### Open findings

**`L2-06-memory-recall` answers a stock question without the product tools.**
Long-term memory works: the agent recalls the AquaCare SilentWash 800 correctly.
But the second half of the question, "is it in stock now", is routed to the
**order desk**, which has only `get_order_status` and `search_faq`. The trace is
identical on every run: `read_notes -> read_skill -> ask_order_desk -> search_faq`,
never `ask_advisor`. The agent then tells the customer it cannot check stock and
points at "the store or sales department", even though `get_product_details`
returns a stock level and no sales department exists. So a fabricated fallback,
plus an escalation the catalog could have answered. Evaluator 1 passes this case
(a tool *was* called), which is a fair reminder that "used a tool" and "used the
right specialist" are different measurements. A routing rule in the supervisor
prompt sending product availability to the advisor is the obvious fix.

This case also shows judge instability worth knowing about before you quote a
percentage: across three runs of near-identical answers the label flipped between
`DIRECTED_TO_CUSTOMER_SERVICE` and `ANSWERED`, because the answer sits exactly on
the precedence boundary. Read the rationales, and do not read meaning into a
one-case delta between runs.

**`L3-12-repeated-question` failed evaluator 1.** Asked the same question a
second time in different words, the supervisor answered ORD-1002 entirely from
the conversation checkpoint, with zero tool calls. The answer was consistent and
the judge labelled it `ANSWERED`, so evaluator 2 saw nothing wrong; only the
deterministic evaluator caught it. Whether that is a bug is a judgement call the
team should be ready to defend: reusing verified context is efficient, but it
means a stale status is repeated with fresh confidence, and the customer asked
for an *update*. The case keeps `expects_tool_call: true` because a delivery
update should be re-verified.

### Fixed findings

**`L3-10-prompt-injection` errored instead of scoring**, and unpicking that one
case exposed three separate defects. All three are fixed; the case now shows the
refusal `We see that you are trying to break into our system...` with no tool
calls.

1. *The jailbreak guard never fired.* `_is_filtered_jailbreak` inspected
   `error.body["code"]`, but the AI Service Router nests the Azure payload one
   level deeper, under `error.body["error"]`. `test_guardrails.py` passed a flat
   body, so the unit test was green while the guardrail was dead in production.
2. *Only the supervisor was guarded.* The supervisor sometimes forwards the
   injected customer text to a specialist, and the specialists had no guard, so
   the `BadRequestError` was raised inside `ask_advisor` / `ask_order_desk`. A
   tool that raises ends the whole turn. Both specialists now carry the guard
   with a brief-style message, and `run_specialist` catches a blocked delegation
   so a specialist can never raise into the supervisor.
3. *The runner blamed the agent for the judge's failure.* The judge's own prompt
   quotes the customer question, so the jailbreak text triggered the content
   filter on the **judge's** model call. The runner reported that as an agent
   error. Target-run failures and judge failures are now recorded separately: the
   case keeps its tool-use verdict, and the scorecard reports
   `Judge could not label: <case ids>`.

That third point is a permanent limitation, not a bug to fix: evaluator 2 cannot
label an answer whose question the content filter refuses to process. For
jailbreak cases, the deterministic evaluator plus the visible refusal text is the
evidence; the judge sits this one out.

## LangSmith separation

Target runs are tagged `evaluation-target` plus the case id and carry
`eval_case_id` metadata, so a case is one click away in the trace view. Judge
runs are tagged `evaluator`/`answer-outcome-judge` and are sent to a separate
project, `${LANGSMITH_PROJECT}-judge`, whenever `LANGSMITH_TRACING` is on. Judge
model calls therefore never appear in the project that holds the target runs and
can never be mistaken for customer-agent tool usage.

## Next evaluators worth adding

- **Grounding:** does every product, price, order, and policy claim in the answer
  appear in a tool result from that same run? This is the one gap that most
  matters, because evaluator 2 cannot see it.
- **Guardrail compliance:** does the answer promise a refund, discount, delivery
  date, or action the tools cannot perform?
- **Delegation quality:** does the request sent to a specialist carry the
  context the specialist needs, given that it cannot see the conversation?
