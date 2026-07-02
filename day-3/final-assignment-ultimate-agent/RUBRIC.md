# Jury Rubric: The Ultimate Agent

100 points total. The jury scores independently, then averages.
Ties are broken by the mystery-shopper round.

## 1. Does it work? (30 points)

| Points | What we see |
|---|---|
| 25 to 30 | All mystery-shopper scenarios handled well, including the nasty ones |
| 15 to 24 | Happy paths work; edge cases (unknown order, angry customer, injection attempt) wobble |
| 5 to 14 | Basic questions work, anything unusual derails it |
| 0 to 4 | Demo gods were not kind today |

## 2. Orchestration & architecture (25 points)

| Points | What we see |
|---|---|
| 20 to 25 | Clear multi-agent design, deliberate pattern choice the team can defend, clean split of responsibilities between agents |
| 12 to 19 | Multiple agents exist but boundaries are fuzzy, or the pattern fights the problem |
| 5 to 11 | Technically two agents, practically one agent with extra steps |
| 0 to 4 | One monolithic agent |

## 3. Harness quality (20 points)

Instructions, tools, skills, memory: the craft of the week.

| Points | What we see |
|---|---|
| 16 to 20 | Sharp system prompts per agent, a genuinely useful self-written tool, memory that demonstrably works, guardrails that hold |
| 10 to 15 | Solid prompts and tools, but e.g. memory is cosmetic or guardrails untested |
| 4 to 9 | Default prompts, self-written tool is trivial |
| 0 to 3 | Harness? What harness? |

## 4. Observability & evaluation (15 points)

| Points | What we see |
|---|---|
| 12 to 15 | Trace walkthrough teaches the jury something; the eval measures something meaningful and the team can interpret its score |
| 7 to 11 | Traces shown, eval runs, but interpretation is thin |
| 3 to 6 | "Here is LangSmith" *(points vaguely at screen)* |
| 0 to 2 | No traces, no eval |

## 5. Demo & creativity (10 points)

| Points | What we see |
|---|---|
| 8 to 10 | Tight demo within time, clear architecture story, and a creative extra that made the jury smile |
| 4 to 7 | Good demo, played it safe |
| 0 to 3 | Overtime, chaos, or "it worked five minutes ago" (we've all been there) |
