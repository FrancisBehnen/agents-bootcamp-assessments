# Day 2 — The Agent Harness

**Goal of the day:** understand what makes a *good* agent: not a smarter
model, but a better **harness** — the instructions, tools, memory and skills
you build around the LLM.

| Part | Assignment | What you build |
|---|---|---|
| Morning | [Assignment 1: Extend your agent](assignment-1-extended-agent/) | Business tools + short & long-term memory |
| Afternoon | [Assignment 2: The skills agent](assignment-2-skills-agent/) | An agent that browses the web and loads skills on demand |

## The core idea of today

Yesterday's agent could call a weather tool. Cute — but real agents at a
company like ours answer questions about **orders, products and policies**,
remember the customer, and follow **procedures**. None of that comes from
the model. All of it comes from the harness:

| Harness element | Question it answers | Today |
|---|---|---|
| Instructions | "Who am I and what are my rules?" | system prompts, morning |
| Tools | "What can I do?" | webshop tools, morning (→ MCP: see below) |
| Memory | "What do I remember?" | checkpointer + notes, morning |
| Skills | "How do I do specific tasks well?" | markdown skills, afternoon |

**Context engineering is the thread through all of it** — every harness
element is a way of getting the *right* information into the context window
at the *right* moment, and keeping the wrong information out.

## About MCP (mentioned in the morning theory)

The tools you use today are Python functions living in this repo. **MCP
(Model Context Protocol)** is an open standard that serves tools from a
separate process/server, so any agent can connect to any tool server —
"USB for tools". Conceptually nothing changes: name, description, schema,
result. If you want to try it after assignment 1, the stretch goal points to
`langchain-mcp-adapters`.

## Show & tell

Same format as yesterday — 5 minutes, from your screen. Today's discussion
focus: **what did you put in the system prompt vs. tools vs. skills, and why?**
