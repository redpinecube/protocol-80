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