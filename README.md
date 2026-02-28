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