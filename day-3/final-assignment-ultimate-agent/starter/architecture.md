# Current Architecture

The starter implements an **agents-as-tools** architecture. A customer talks to one
supervisor agent through a command-line loop. The supervisor decides whether to
answer directly, use memory, or delegate domain work to one of two specialist
agents. Each specialist is exposed to the supervisor as a normal LangChain tool.

## Architecture at a Glance

```mermaid
flowchart TB
    Customer([Customer]) <--> Supervisor[Supervisor]
    Supervisor <--> Advisor[Product advisor]
    Supervisor <--> OrderDesk[Order desk]

    subgraph Harness[Shared harness]
        ProductTools[Product tools<br/>search_products<br/>get_product_details<br/>compare_replacement_products]
        ServiceTools[Service tools<br/>get_order_status<br/>search_faq]
        MemoryTools[Memory tools<br/>save_note<br/>read_notes]
        OtherTools[Other implemented tools<br/>calculator<br/>get_weather<br/>fetch_webpage<br/>list_skills<br/>read_skill]
        Data[(Mock data<br/>products, orders, FAQ)]
        MemoryFile[(Long-term notes<br/>.agent_memory.json)]
        LLM[get_llm<br/>AI Service Router client]

        ProductTools --> Data
        ServiceTools --> Data
        MemoryTools <--> MemoryFile
    end

    Advisor --> ProductTools
    OrderDesk --> ServiceTools
    Supervisor --> MemoryTools
    Supervisor -.-> LLM
    Advisor -.-> LLM
    OrderDesk -.-> LLM
```

## Evaluation at a Glance

Two offline evaluators run around a complete supervisor invocation. See
[evaluation/README.md](evaluation/README.md) for the design, the dataset, and how to read the
scorecard.

```mermaid
flowchart LR
    Scenarios[(Evaluation scenarios)] --> Runner[Evaluation runner]
    Runner -->|question and fresh thread| Supervisor[Supervisor]
    Supervisor --> Result[Final answer and trace]
    Result --> ToolEval[Tool called before answer?]
    Result --> AnswerEval[Customer question outcome]
    ToolEval --> Scorecard[(Evaluation scorecard)]
    AnswerEval --> Scorecard
```

## Detailed Architecture

```mermaid
flowchart TB
    Customer([Customer]) -->|terminal input| CLI[CLI loop<br/>starter/main.py]

    subgraph Application[Ultimate Agent starter]
        CLI -->|message and thread_id: demo| Supervisor[Supervisor agent<br/>customer-service coordinator]
        Supervisor <--> Checkpointer[(InMemorySaver<br/>conversation checkpoints)]

        Supervisor -->|tool call with relevant context| AskAdvisor[ask_advisor tool]
        Supervisor -->|tool call with relevant context| AskOrderDesk[ask_order_desk tool]
        AskAdvisor --> Advisor[Product advisor agent]
        AskOrderDesk --> OrderDesk[Order desk agent]
        Advisor -->|final specialist message| AskAdvisor
        OrderDesk -->|final specialist message| AskOrderDesk
        AskAdvisor -->|tool result| Supervisor
        AskOrderDesk -->|tool result| Supervisor
        Supervisor -->|final response| CLI
    end

    subgraph Harness[Shared harness package]
        GetLLM[get_llm]

        subgraph WebshopTools[Webshop tools]
            SearchProducts[search_products]
            ProductDetails[get_product_details]
            CompareProducts[compare_replacement_products<br/>custom tool]
            OrderStatus[get_order_status]
            SearchFAQ[search_faq]
        end

        subgraph MemoryTools[Long-term memory tools]
            SaveNote[save_note]
            ReadNotes[read_notes]
        end

        MockData[(harness.data<br/>PRODUCTS, ORDERS, FAQ)]
        NotesFile[(.agent_memory.json)]

        SearchProducts --> MockData
        ProductDetails --> MockData
        CompareProducts --> MockData
        OrderStatus --> MockData
        SearchFAQ --> MockData
        SaveNote <--> NotesFile
        ReadNotes <--> NotesFile
    end

    Advisor --> SearchProducts
    Advisor --> ProductDetails
    Advisor --> CompareProducts
    OrderDesk --> OrderStatus
    OrderDesk --> SearchFAQ
    Supervisor --> SaveNote
    Supervisor --> ReadNotes

    Supervisor -. model calls .-> GetLLM
    Advisor -. model calls .-> GetLLM
    OrderDesk -. model calls .-> GetLLM
    GetLLM -->|OpenAI-compatible API| Router[Coolblue AI Service Router]
    Router --> Model[Configured chat model]
    Environment[.env configuration] --> GetLLM
```

## Replacement Flow

```mermaid
sequenceDiagram
    actor Customer
    participant Supervisor
    participant OrderDesk as Order desk
    participant Advisor as Product advisor
    participant CompareTool as compare_replacement_products

    alt Customer names the broken product
        Customer->>Supervisor: My AEG washing machine is broken; find a replacement
        Supervisor->>Advisor: Find a replacement for the named washing machine
    else Customer refers only to an order
        Customer->>Supervisor: Find a replacement for the product in ORD-1003
        Supervisor->>OrderDesk: Identify the product in ORD-1003
        OrderDesk-->>Supervisor: FreshSpin 8000 Washing Machine
        Supervisor->>Advisor: Find a replacement for FreshSpin 8000 Washing Machine
    end
    Advisor->>CompareTool: Compare the source product with the catalog
    CompareTool-->>Advisor: Similar products from the same category only
    Advisor-->>Supervisor: Grounded replacement recommendation
    Supervisor-->>Customer: Recommended replacement and rationale
```

## Components

### Command-line interface

`main.py` runs a synchronous read-evaluate-print loop. Every non-empty customer
message is sent to the supervisor with one LangGraph thread ID generated per
process start, so each run is a fresh conversation. The last message returned by
the supervisor is printed as the CoolShop response.

### Supervisor

The supervisor is a LangChain agent created with `create_agent`. It owns the
customer-facing conversation and can call four tools:

- `ask_advisor` for product discovery and recommendations.
- `ask_order_desk` for orders, delivery, returns, and store policy.
- `save_note` to persist a durable customer fact.
- `read_notes` to retrieve durable facts from earlier conversations.

The supervisor must include all relevant conversation details in a delegation.
Specialists cannot inspect the supervisor's conversation history and receive only
the `request` string supplied in their tool call.

For replacement requests that mention only an order number, the supervisor must
orchestrate two specialists in sequence. It first asks the order desk to identify
the product in the order, then includes that product information when asking the
product advisor for a replacement. It must not ask the advisor to infer or invent
the missing product.

### Specialist agents

The product advisor can call `search_products`, `get_product_details`, and the
custom tool `compare_replacement_products`. Search supports progressive
disclosure by returning compact catalog results before the agent requests complete
specifications for a selected product.

`compare_replacement_products` accepts information about a broken or existing
product and finds the most similar replacements in the CoolShop catalog. It must
first determine the source product's category and return candidates from that same
category only. For example, replacing an AEG washing machine can produce only
washing-machine candidates, ranked by relevant similarity such as capacity,
energy label, dimensions, features, price, and availability. If the source category
cannot be determined, the tool returns no candidates and asks for more product
information rather than searching across categories.

The order desk can call `get_order_status` and `search_faq`. Order lookup returns
mock operational data, while FAQ search retrieves up to two keyword-ranked policy
entries.

Neither specialist has a checkpointer or memory tools. Each invocation starts with
only the delegated request and runs its own model/tool loop until it produces a
final answer. The wrapper returns only that final message to the supervisor.

## Harness Responsibilities

The shared `harness` package supplies infrastructure used by the agents:

- `harness.llm.get_llm` loads the repository `.env`, selects `BOOTCAMP_MODEL`,
  and creates a `ChatOpenAI` client for the Coolblue AI Service Router.
- `harness.tools` exports LangChain tools and themed bundles. The starter imports
    the five webshop tools directly and expands `MEMORY_TOOLS` for the supervisor.
    The comparison tool is included in `WEBSHOP_TOOLS` and attached to the advisor.
- `harness.data` contains the in-process `PRODUCTS`, `ORDERS`, and `FAQ` fixtures
  read by the webshop tools. No external commerce service is called.
- `harness.tools.memory` stores long-term notes in `.agent_memory.json` relative
  to the process's current working directory.

The harness also offers calculator, weather, web, and skill tools, but the current
starter does not attach them to any agent.

## State and Data Lifetime

There are two independent forms of memory:

| State | Owner | Storage | Lifetime |
| --- | --- | --- | --- |
| Conversation messages | Supervisor | `InMemorySaver` checkpoint keyed by `thread_id` | Current Python process |
| Durable customer notes | Supervisor memory tools | `.agent_memory.json` | Across process restarts and conversations |

The product catalog, orders, and FAQ are static Python fixtures. Changes exist only
when the source data is edited; the current tools do not mutate webshop data.

## Current Extension Points

The file intentionally remains starter scaffolding. The order-desk and supervisor
prompts still contain team TODOs. `compare_replacement_products` is implemented and
registered with the product advisor. The two evaluators, the runner, and the
evaluation dataset are implemented in the `evaluation/` folder; see
[evaluation/README.md](evaluation/README.md). No third specialist is
present. LangSmith tracing can observe LangChain calls when configured through the
environment, but explicit observability setup is not part of `main.py`; the
evaluation runner adds its own tags, metadata, and separate judge project.
