# Agentic AI Customer Support Mini Project

A beginner-friendly end-to-end project using **FastAPI, LangGraph, an LLM, and RAG with FAISS**.

## What it does

- Accepts a customer message through a FastAPI endpoint.
- Uses an LLM supervisor to decide whether to check an order, search policy documents, or do both.
- Runs the selected specialist nodes in a LangGraph workflow. Order and policy checks can run in parallel.
- Uses FAISS retrieval over `data/policies.txt` for policy-grounded answers.
- Combines the results into a final customer-support response.
- Includes a small in-memory order database for practice.

> This is a learning demo, not a production refund processor. It does not actually issue refunds or modify orders.

## 1. Requirements

- Python 3.10 or newer
- An OpenAI API key with API access and billing enabled

## 2. Open the project

Extract `agentic-support-system.zip`, then open the extracted `agentic-support-system` folder in VS Code.

## 3. Create and activate a virtual environment

### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt:
```bat
.venv\Scripts\activate.bat
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure your API key

Copy `.env.example` to a new file named `.env` and replace the placeholder:

```env
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-4o-mini
```

Keep `.env` private. Do not commit it or share screenshots that reveal your key.

## 6. Run the API

From the project root:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to test the API using Swagger UI.

## 7. Try these requests

Use `POST /chat` with a JSON body.

### Order status
```json
{
  "message": "Where is order ORD-1001?"
}
```

### Refund policy
```json
{
  "message": "Can I get a refund within 30 days?"
}
```

### Combined request
```json
{
  "message": "Check order ORD-1002 and tell me whether the refund policy may apply."
}
```

### Health check
Open `http://127.0.0.1:8000/health`.

## Project layout

```text
agentic-support-system/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI routes
│   ├── schemas.py              # Request/response validation
│   ├── state.py                # LangGraph state
│   ├── graph.py                # Supervisor, routing, and workflow
│   └── tools/
│       ├── __init__.py
│       ├── order_tools.py      # Demo order lookup
│       └── knowledge_tools.py  # Policy RAG with FAISS
├── data/
│   └── policies.txt
├── .env.example
├── .gitignore
└── requirements.txt
```

## What to learn from this project

1. **RAG:** load policy text → split into chunks → create embeddings → index in FAISS → retrieve relevant chunks.
2. **State:** the shared LangGraph state carries the request and each node's result.
3. **Node:** each node is a function that performs one task.
4. **Conditional routing:** the supervisor chooses which specialist nodes to run.
5. **Parallel execution:** when both order and policy information are needed, the graph can run those branches in parallel.
6. **Grounded response:** the final response is instructed to use the retrieved policy/order data and say when information is insufficient.

## Troubleshooting

- **Missing API key:** ensure `.env` exists in the project root and contains a valid `OPENAI_API_KEY`.
- **FAISS install issue on Windows:** use a recent 64-bit Python version and upgrade pip. If installation still fails, use a Python virtual environment with a supported Python version.
- **Model access or quota error:** verify your API key, API billing, and the model name in `.env`.
- **Import errors:** activate the virtual environment and run `pip install -r requirements.txt` again.
- The first policy search creates embeddings through the OpenAI API, so it uses API credits. This demo rebuilds the small FAISS index when the server process starts.
