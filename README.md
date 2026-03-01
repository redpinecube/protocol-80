
# 🤖 RateMyAPI (v1.0.0)

> **The storefront for the 2026 Agentic Economy.**

**RateMyAPI** is a developer-first tool designed to audit, score, and optimize web services for AI-agent interoperability. In an era where web traffic is increasingly driven by autonomous agents rather than humans, your API’s usability is your most critical business metric.

---

## 🛠 Infrastructure

* 🔵 **Gemini 1.5 Flash** — Core Evaluation & Reasoning Engine
* 🟠 **Django / Python 3.13** — Backend Framework
* ⚪ **DigitalOcean** — High-Availability Cloud Hosting

---

## 📊 Agentic Readiness Score (ARS)

We evaluate APIs based on five core criteria. Each is rated **0–10** by Gemini and combined via weighted average into a final **ARS**.

| Criterion | Weight | Description |
| --- | --- | --- |
| **Semantic Clarity** | 25% | Are endpoint names and fields self-describing for an LLM? |
| **Type Accuracy** | 25% | Are request/response schemas strict, typed, and unambiguous? |
| **Token Efficiency** | 20% | How many tokens does a standard interaction cost an agent? |
| **Idempotency Safety** | 15% | Does it support `Idempotency-Key` headers for safe retries? |
| **Documentation Clarity** | 15% | Can an agent self-integrate without human intervention? |

---

## 💻 Developer Setup

1. **Environment:** Create and activate a Python virtual environment.
```bash
python3 -m venv .venv
source .venv/bin/activate

```


2. **Dependencies:** Install the required packages.
```bash
pip install -r requirements.txt

```


3. **Backend:** Start the Django development server.
```bash
cd api
python manage.py runserver

```


*The server must be running to process CLI requests.*

---

## ⌨️ CLI Usage

Run the CLI from the repository root. Ensure your backend server is active (default: `http://127.0.0.1:8000`).

```bash
# Check API health
python ratemyapi_cli.py health

# Evaluate an API for AI usability
# Use --timeout 60 to allow the AI sufficient processing time
python ratemyapi_cli.py evaluate --body https://api.example.com/v1/docs \
  --timeout 60 \
  --documentation \
  --response-format json

# Get detailed analysis and remediation steps
python ratemyapi_cli.py analyze --body https://api.example.com/v1/docs \
  --timeout 60

# Run Django management commands via CLI
python ratemyapi_cli.py manage migrate

```

---

## 🚀 API Reference

### 1. Create Evaluation

`POST /api/evaluate/`

Submits an API for audit. Note: This is an intensive process; use a higher timeout on the client side.

**Request Body:**

```json
{
  "api_url": "https://api.example.com/v2/openapi.json",
  "auth_type": "bearer",
  "docs_format": "openapi",
  "environment": "prod"
}

```

**Success Response (`200 OK`):**

```json
{
  "service": "ratemyapi",
  "object": "evaluation",
  "score": 85,
  "comment": "Strong semantic clarity, but lacks idempotency keys on POST requests.",
  "status": "completed"
}

```

### 2. Deep Analysis

`POST /api/analyze/`

Provides a granular breakdown of "friction points" that would prevent an AI agent from successfully using the API.

**Success Response (`200 OK`):**

```json
{
  "service": "ratemyapi",
  "object": "analysis_report",
  "findings": ["Inconsistent snake_case usage", "Missing 429 rate limit documentation"],
  "remediation_plan": "1. Standardize all keys to snake_case. 2. Define rate limits in headers.",
  "agent_friction": "Agent may struggle to handle unexpected HTML error pages during 500 errors."
}

```

---

## 🤝 Contributing

Built for the 2026 Agentic Economy.

[GitHub](https://www.google.com/search?q=https://github.com/your-username/ratemyapi) · [Changelog](https://www.google.com/search?q=%23) · [Team](mailto:team@ratemyapi.tech)

© 2026 RateMyAPI. Released under the MIT License.
