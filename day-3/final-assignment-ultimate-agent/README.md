# 🏆 Day 3 · Final Assignment — Build the Ultimate Agent

⏱️ all day (~5 hours) · 👥 teams of 3–4 · 🎤 demo at 15:00 · 🏅 prizes!

## The mission

CoolShop's management has seen your work this week and wants **one** system
customers can talk to for *everything*: product advice, order questions,
complaints, policies — the works. Your team builds it.

You have the full harness at your disposal (all tools, the skills mechanism,
memory, and everything you built this week). How you architect it is **your
call** — that's the assignment.

## Hard requirements (the jury checks all of these)

1. **Multi-agent orchestration.** At least **two specialised agents** (or
   agent-nodes) plus something that coordinates them. Any pattern from this
   morning is fine — supervisor, agents-as-tools, hybrid workflow, handoffs.
2. **At least one self-written tool.** Something that doesn't exist in the
   harness yet. Ideas: `create_return_label`, `check_delivery_slots`,
   `apply_price_alert` — or something we didn't think of (better!).
3. **Memory.** The system remembers the conversation (short-term), and
   at least one thing across conversations (long-term).
4. **Observability.** You can show your system's behaviour in LangSmith and
   use a trace to explain one interesting decision it made.
5. **One evaluation.** You learned LLM-as-a-judge in the previous sprint —
   use it. Write ONE evaluator (e.g. "was the answer grounded in tool
   results?") and run it over the test scenarios. A simple script is enough;
   what matters is that you *measured* something.
6. **It survives the mystery shopper.** See
   [test_scenarios.md](test_scenarios.md) — the jury will run a selection of
   these against your system live, including the nasty ones.

## Freedom (please use it)

- Any orchestration pattern, any number of agents.
- Add your own skills, your own data, your own personality.
- A creative extra feature is explicitly rewarded in the rubric — surprise us.

## The demo (5 minutes per team, strict)

1. **30 sec** — your architecture, on one diagram (whiteboard photo is fine).
2. **2 min** — live demo: your best scenario + one scenario the jury picks.
3. **1 min** — one LangSmith trace: walk us through an interesting decision.
4. **1 min** — your eval: what did you measure, what did it score?
5. **30 sec** — what you'd build next with one more week.

## Scoring

See [RUBRIC.md](RUBRIC.md) — the jury scores five categories, 100 points
total. Read it *before* you start building: it's effectively the assignment
in checklist form. The winning team gets eternal fame and an actual prize.

## Practical tips from people who have built these before

- **Start with the dumbest thing that works** — one supervisor +
  two specialists — and iterate. Teams that architect for two hours demo
  nothing at 15:00.
- **Split the work by agent.** Each teammate owns a specialist end-to-end
  (prompt, tools, tests). Integrate every hour.
- **Use the starter** ([starter/main.py](starter/main.py)) if you want
  scaffolding for the agents-as-tools pattern; ignore it if you don't.
- **Traces > print statements.** When routing goes wrong (it will), the
  trace shows you where in seconds.
- **Freeze at 14:30.** The last 30 minutes are for rehearsing the demo, not
  for one more feature. Nobody demos a feature they built at 14:55.
