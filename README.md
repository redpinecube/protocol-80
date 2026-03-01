# protocol 80
Protocol 80 is a developer-first API designed to audit, score, and optimize your web services for the 2026 Agentic Economy.
As the web shifts from human-centric browsing to AI-agent transactions, your API useability is now your most important storefront. 

# dev set-up 
set up a python virtual environment. 

use the following command to install dependencies :
pip install -r requirements.txt

use python manage.py runserver to start backend server

# CLI
Use the project CLI from the repository root:

```bash
# Check API health
python protocol80_cli.py health

# Evaluate your API for AI usability
python protocol80_cli.py evaluate https://myapi.com \
  --endpoints /users,/products,/orders \
  --documentation \
  --response-format json \
  --authentication \
  --error-handling \
  --versioning

# Get quick score
python protocol80_cli.py score https://myapi.com \
  --endpoints /users,/products \
  --documentation \
  --authentication

# Get detailed analysis with recommendations
python protocol80_cli.py analyze https://myapi.com \
  --documentation \
  --response-format json

# Make custom API requests
python protocol80_cli.py request GET /health/
python protocol80_cli.py request GET /
python protocol80_cli.py request POST /api/evaluate/ --data '{"api_url": "https://example.com"}'

# Run Django management commands through CLI
python protocol80_cli.py manage migrate
python protocol80_cli.py manage runserver
```

## Available API Endpoints
When the server is running (default: http://127.0.0.1:8000):
- `GET /` - API index with endpoint list
- `GET /health/` - Health check
- `POST /api/evaluate/` - Evaluate API usability (full report)
- `POST /api/score/` - Get quick usability score
- `POST /api/analyze/` - Get detailed analysis with recommendations
- `/admin/` - Django admin interface

## Auto Deploy to DigitalOcean
This repo includes a GitHub Actions workflow at `.github/workflows/deploy-digitalocean.yml`.

It deploys automatically whenever code is pushed to the `dev` branch.

### Required GitHub Secrets
In GitHub: **Settings → Secrets and variables → Actions → New repository secret**

- `DO_HOST` = your droplet IP (example: `104.236.211.164`)
- `DO_USERNAME` = SSH user (example: `root`)
- `DO_PASSWORD` = SSH password for that user

### What the workflow does
On each push to `dev`, it will:
1. SSH into your droplet
2. Reset `/home/protocol-80` to latest `origin/dev`
3. Run Django migrations
4. Collect static files
5. Restart the `protocol80` systemd service

-----

# Documentation
---

# 🤖 Protocol 80 (v1.0.0)

> **The storefront for the 2026 Agentic Economy.**

**Protocol 80** is a developer-first API designed to audit, score, and optimize your web services for the AI-agent era. As the web shifts from human-centric browsing to autonomous agent transactions, your API's usability is now its most critical storefront.

**Base URL:** `https://ratemyapi.tech`

---

## 🛠 Infrastructure

* 🔵 **Gemini API** — Core Evaluation & Reasoning Engine
* 🟠 **DigitalOcean** — High-Availability Deployment

---

## 📊 Agentic Readiness Score

We evaluate APIs based on five core criteria. Each is rated **0–10** by Gemini and combined via weighted average into a final score.

| Criterion | Weight | Description |
| --- | --- | --- |
| **Semantic Clarity** | 25% | Are endpoint names and fields self-describing for an LLM? |
| **Type Accuracy** | 25% | Are request/response schemas strict, typed, and unambiguous? |
| **Token Efficiency** | 20% | How many tokens does a standard interaction cost an agent? |
| **Idempotency Safety** | 15% | Does it support `Idempotency-Key` headers for safe retries? |
| **Documentation Clarity** | 15% | Can an agent self-integrate without human intervention? |

---

## 🚀 API Reference

### 1. Create Evaluation

`POST /evaluate`

Submit an API endpoint or OpenAPI spec for analysis. Evaluations are processed asynchronously.

#### Headers

| Name | Type | Description |
| --- | --- | --- |
| `Content-Type` | `string` | **Required.** Must be `application/json`. |
| `Idempotency-Key` | `string` | **Recommended.** Unique UUID v4 to prevent duplicate billing on retries. |

#### Request Body

| Field | Type | Description |
| --- | --- | --- |
| `url` | `string` | **Required.** The target API base URL or spec URL. |
| `method` | `string` | HTTP method to test (GET, POST, etc.). Defaults to `GET`. |
| `headers` | `object` | Optional headers for probing the endpoint. |
| `body` | `object` | Optional request body for write methods. |
| `callback_url` | `string` | Webhook URL to receive results upon completion. |

#### Example Request

```bash
curl -X POST https://ratemyapi.tech/api/evaluate \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000" \
  -d '{
    "url": "https://api.example.com/v2/openapi.json",
    "method": "POST"
  }'

```

#### Responses

* **`201 Created`**: Evaluation job started.
```json
{
  "id": "eval_a1b2c3d4e5f6",
  "status": "processing",
  "created_at": "2026-02-28T14:30:00Z",
  "estimated_seconds": 12
}

```


* **`409 Conflict`**: Duplicate request (existing `Idempotency-Key`).
* **`422 Unprocessable Entity`**: Invalid URL or unsupported parameters.

---

### 2. Retrieve Results

`GET /evaluate/{id}`

Fetch the status or results of a previously submitted evaluation.

#### Path Parameters

| Name | Type | Description |
| --- | --- | --- |
| `id` | `string` | **Required.** The evaluation ID (format: `eval_*`). |

#### Example Response (Status: Completed)

```json
{
  "id": "eval_a1b2c3d4e5f6",
  "status": "completed",
  "agentic_readiness_score": 7.4,
  "breakdown": {
    "semantic_clarity": { "score": 8, "weight": 0.25 },
    "type_accuracy": { "score": 9, "weight": 0.25 },
    "token_efficiency": { "score": 6, "weight": 0.20 },
    "idempotency_safety": { "score": 5, "weight": 0.15 },
    "documentation_clarity": { "score": 8, "weight": 0.15 }
  },
  "recommendations": [
    "Add Idempotency-Key support to POST endpoints",
    "Reduce response payload — 40% of fields are unused by agents"
  ],
  "evaluated_at": "2026-02-28T14:30:12Z"
}

```

#### Example Response (Status: Processing)

```json
{
  "id": "eval_a1b2c3d4e5f6",
  "status": "processing",
  "progress": 0.65,
  "estimated_seconds_remaining": 4
}

```

---

## 🤝 Contributing

Built for the agentic economy.
[GitHub](https://www.google.com/search?q=%23) · [Changelog](https://www.google.com/search?q=%23) · [Team](mailto:team@protocol80.dev)

© 2026 Protocol 80. Released under the MIT License.
