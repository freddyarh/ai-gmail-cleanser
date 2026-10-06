# AI Gmail Cleanser Agent

A modular Python project for an **AI Portfolio**: connect to Gmail, parse unread mail, classify it with an LLM, and safely triage the inbox with labels and archive actions—without blindly deleting email.

Built in three phases:

| Phase | Script | What it does |
|-------|--------|----------------|
| **1** | `data_pipeline.py` | OAuth2, fetch unread mail, parse to clean dicts |
| **2** | `agent.py` | LLM classification (no Gmail writes) |
| **3** | `cleanser.py` | Labels, archive, **label-first** delete workflow |

---

## Features

- **Gmail API** integration with OAuth2 (`credentials.json` → `token.json`)
- **Structured parsing**: `id`, `sender`, `subject`, `snippet` (HTML/signatures stripped)
- **LLM triage**: category, priority, recommended action, confidence, summary
- **Job offers**: category `job_offer` with focus `software` | `ai_ml` | `other`
- **Safe Phase 3**: delete suggestions become `AI/Pending Delete`; trash only on a second, confirmed pass
- **Audit log**: `logs/actions.json`
- **SOLID-style action layer**: policy, handlers, label repository

---

## Tech stack

- Python 3.10+
- [Google Gmail API](https://developers.google.com/gmail/api) (`google-api-python-client`)
- [OpenAI API](https://platform.openai.com/) (JSON-mode classification)
- `python-dotenv` for configuration

---

## Project structure

```text
email-automation/
├── data_pipeline.py      # Phase 1 — fetch & parse
├── agent.py              # Phase 2 — classify only
├── cleanser.py           # Phase 3 — classify + Gmail actions
├── classifier/
│   ├── llm_client.py
│   ├── prompts.py
│   └── classify.py
├── actions/
│   ├── policy.py         # safety rules
│   ├── label_names.py
│   ├── label_repository.py
│   ├── handlers.py
│   ├── executor.py
│   ├── pending_delete.py
│   └── log.py
├── config/
│   └── settings.py
├── requirements.txt
├── .env.example
└── logs/                 # gitignored
