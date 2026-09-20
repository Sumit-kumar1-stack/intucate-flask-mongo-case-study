# Vercel Deployment

This repository can run as a Flask application on Vercel.

## Project configuration

- Repository: `intucate-flask-mongo-case-study`
- Root Directory: `./`
- Framework: Flask / auto-detect
- Entry point: `app:app`

## Environment variables

```env
MONGO_URI=mongodb+srv://...
MONGO_DB_NAME=intucate_case_study
AI_PROVIDER=mock
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
MAX_INPUT_CHARS=4000
MAX_BATCH_SIZE=25
```

For a zero-cost/demo deployment, keep `AI_PROVIDER=mock`. If using an external AI provider, set the corresponding secret in Vercel rather than committing it.

MongoDB must be a network-accessible hosted database; `mongodb://localhost:27017` is only a local-development default.

## Verification

1. Root/API endpoint responds over HTTPS.
2. MongoDB connection succeeds.
3. Mock AI flow works without an external API key.
4. If OpenAI is enabled, the key exists only in Vercel environment variables.
5. Runtime logs contain no credentials or user-sensitive payloads.
