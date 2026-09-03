# Flask + MongoDB Prompt Service (Reference Implementation)

> This repository is a learning/reference implementation for the provided case-study requirements. If the assessment requires original work, understand the design and implement/adapt it yourself before submitting.

## What it demonstrates

- Flask POST endpoint for one `userInput`
- Prompt template loaded from MongoDB `prompts`
- `{{userInput}}` substitution
- Pluggable AI provider (`mock` by default, optional OpenAI)
- One MongoDB `history` document per request/response pair
- Batch POST endpoint using `asyncio.gather()` for concurrent AI calls
- Output order preserved to match input order
- Validation and normalized API errors
- Unit/API tests that do not require MongoDB or an AI key

## Architecture

```text
HTTP client
   |
   v
Flask routes
   |
   v
PromptService  -----> AIProvider
   |
   +-----> PromptRepository -----> MongoDB/prompts
   |
   +-----> HistoryRepository ---> MongoDB/history
```

### Why these layers?

- `routes`: HTTP parsing and status codes only.
- `services`: business rules, prompt rendering, concurrency, persistence orchestration.
- `repositories`: database-specific queries.
- `AIProvider`: isolates external AI integration so a mock can be used locally and in tests.

## Project structure

```text
.
├── app.py
├── config.py
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── scripts/
│   └── seed_prompt.py
├── src/
│   ├── api/routes.py
│   ├── domain/errors.py
│   ├── repositories/mongo.py
│   ├── services/ai_provider.py
│   ├── services/prompt_service.py
│   └── app_factory.py
└── tests/
    ├── fakes.py
    └── test_api.py
```

## Prerequisites

- Python 3.11 or newer
- MongoDB locally **or** Docker Desktop
- Optional: OpenAI API key if you choose `AI_PROVIDER=openai`

## Windows setup (recommended)

### 1. Extract and enter the project

```bat
cd intucate_flask_mongo_reference
```

### 2. Create a virtual environment

```bat
py -m venv .venv
.venv\Scripts\activate
```

If `py` is unavailable, try `python` instead.

### 3. Install packages

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create your local environment file

Command Prompt:

```bat
copy .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

The default uses `AI_PROVIDER=mock`, so no paid AI key is required.

### 5. Start MongoDB

If using Docker Desktop:

```bat
docker compose up -d mongo
```

Check it:

```bat
docker compose ps
```

If you already run MongoDB on Windows, leave `MONGO_URI=mongodb://localhost:27017` in `.env` and skip Docker.

### 6. Seed the required prompt document

```bat
python scripts\seed_prompt.py
```

Expected output:

```text
Seeded prompt: Education_Prompt
```

### 7. Run tests

```bat
pytest -q
```

Expected result: all tests pass.

### 8. Start Flask

```bat
python app.py
```

Default URL:

```text
http://127.0.0.1:5000
```

## Check locally

### Health endpoint

Open in browser:

```text
http://127.0.0.1:5000/health
```

Expected:

```json
{
  "database": "reachable",
  "status": "ok"
}
```

### Single request

PowerShell:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:5000/api/v1/generate `
  -ContentType 'application/json' `
  -Body '{"userInput":"How much should I score in each subject to pass CA final?"}'
```

Command Prompt with curl:

```bat
curl -X POST http://127.0.0.1:5000/api/v1/generate -H "Content-Type: application/json" -d "{\"userInput\":\"How much should I score in each subject to pass CA final?\"}"
```

With the mock provider, the response is intentionally deterministic and local.

### Batch request

PowerShell:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:5000/api/v1/generate/batch `
  -ContentType 'application/json' `
  -Body '{"userInputs":["Explain Flask","Explain MongoDB","Explain asyncio"]}'
```

Expected shape:

```json
{
  "responses": [
    "...response for item 1...",
    "...response for item 2...",
    "...response for item 3..."
  ]
}
```

The response list follows the same order as `userInputs`.

## MongoDB collections

### `prompts`

Seeded example:

```json
{
  "_id": "Education_Prompt",
  "template": "You are an expert in education domain. Answer the following: {{userInput}}"
}
```

### `history`

One document is saved for every individual AI call. Example fields:

```json
{
  "request_id": "uuid",
  "request_type": "single",
  "item_index": null,
  "prompt_id": "Education_Prompt",
  "user_input": "What is Flask?",
  "final_prompt": "You are an expert ... What is Flask?",
  "response": "...",
  "created_at": "UTC datetime"
}
```

For a batch, all items share a `request_id` and receive `item_index` values `0..n-1`.

## Why `asyncio.gather()`?

AI requests are independent I/O-bound operations. `asyncio.gather()` starts the item coroutines concurrently instead of waiting for one network response before starting the next. It also returns results in the order of the awaitables supplied to it, satisfying the case-study requirement that the returned list match the input order.

MongoDB operations in PyMongo are synchronous, so the service sends them through `asyncio.to_thread(...)` rather than blocking the event loop while an AI call is active.

## Optional OpenAI mode

Edit `.env`:

```text
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Install the optional provider first:

```bat
pip install -r requirements-openai.txt
```

Then restart Flask. Keep `.env` out of Git; `.gitignore` already excludes it.

## Error examples

Empty input:

```json
{
  "error": "userInput cannot be empty"
}
```

Wrong batch type:

```json
{
  "error": "userInputs must be a list of strings"
}
```

## Useful interview explanations

**Why store the template in MongoDB?**  
It treats the prompt as configurable data rather than hard-coded application logic. Prompt text can change without editing service code.

**Why one history document per AI call?**  
It directly models the request/response pair required by the assignment and keeps querying, auditing, and debugging simple. Batch calls are correlated with `request_id`.

**Why use dependency injection in tests?**  
The app factory accepts fake repositories and a fake AI provider, which lets tests verify API and service behavior without requiring MongoDB or external network calls.

**Why fetch one template for a batch?**  
The batch is one incoming API request and all items use the same configured prompt. Fetching once avoids duplicate database reads while still satisfying the requirement that the prompt comes from NoSQL.

## Production improvements

For a larger production system, consider request tracing, structured logging, retry/backoff for transient AI failures, timeouts, rate limits, authentication, secret management, MongoDB indexes based on actual query patterns, and a production WSGI/ASGI deployment strategy.
