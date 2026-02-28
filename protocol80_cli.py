#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib import error, parse, request


DEFAULT_API_URL = os.environ.get("PROTOCOL80_API_URL", "http://127.0.0.1:8000")
PROJECT_ROOT = Path(__file__).resolve().parent
MANAGE_PY = PROJECT_ROOT / "api" / "manage.py"


def normalize_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/")
    suffix = path if path.startswith("/") else f"/{path}"
    return f"{base}{suffix}"


def cmd_health(args: argparse.Namespace) -> int:
    url = normalize_url(args.base_url, "/health/")
    req = request.Request(url, method="GET")

    try:
        with request.urlopen(req, timeout=args.timeout) as resp:
            body = resp.read().decode("utf-8")
            payload = json.loads(body)
            print(json.dumps(payload, indent=2))
            return 0
    except error.URLError as exc:
        print(f"Health check failed: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError:
        print("Health check response was not valid JSON", file=sys.stderr)
        return 1


def cmd_request(args: argparse.Namespace) -> int:
    url = normalize_url(args.base_url, args.path)
    headers = {"Accept": "application/json"}

    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"

    body = None
    if args.data:
        headers["Content-Type"] = "application/json"
        body = args.data.encode("utf-8")

    req = request.Request(url, data=body, headers=headers, method=args.method.upper())

    try:
        with request.urlopen(req, timeout=args.timeout) as resp:
            response_body = resp.read().decode("utf-8")
            if not response_body:
                print("{}")
                return 0
            try:
                print(json.dumps(json.loads(response_body), indent=2))
            except json.JSONDecodeError:
                print(response_body)
            return 0
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8") if exc.fp else ""
        print(f"Request failed: {exc.code} {exc.reason}", file=sys.stderr)
        if error_body:
            print(error_body, file=sys.stderr)
        return 1
    except error.URLError as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1


def cmd_manage(args: argparse.Namespace) -> int:
    if not MANAGE_PY.exists():
        print(f"manage.py not found at {MANAGE_PY}", file=sys.stderr)
        return 1

    command = [sys.executable, str(MANAGE_PY), *args.manage_args]
    result = subprocess.run(command, cwd=PROJECT_ROOT)
    return result.returncode


def cmd_evaluate(args: argparse.Namespace) -> int:
    """Evaluate API usability and get full report"""
    url = normalize_url(args.base_url, "/api/evaluate/")
    
    payload = {
        "api_url": args.api_url,
        "endpoints": args.endpoints.split(",") if args.endpoints else [],
        "documentation": args.documentation,
        "response_format": args.response_format or "json",
        "authentication": args.authentication,
        "error_handling": args.error_handling,
        "versioning": args.versioning,
    }
    
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers=headers, method="POST")
    
    try:
        with request.urlopen(req, timeout=args.timeout) as resp:
            response_body = resp.read().decode("utf-8")
            result = json.loads(response_body)
            print(json.dumps(result, indent=2))
            return 0
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8") if exc.fp else ""
        print(f"Evaluation failed: {exc.code} {exc.reason}", file=sys.stderr)
        if error_body:
            print(error_body, file=sys.stderr)
        return 1
    except error.URLError as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        return 1


def cmd_score(args: argparse.Namespace) -> int:
    """Get usability score for an API"""
    url = normalize_url(args.base_url, "/api/score/")
    
    payload = {
        "api_url": args.api_url,
        "endpoints": args.endpoints.split(",") if args.endpoints else [],
        "documentation": args.documentation,
        "response_format": args.response_format or "json",
        "authentication": args.authentication,
        "error_handling": args.error_handling,
        "versioning": args.versioning,
    }
    
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers=headers, method="POST")
    
    try:
        with request.urlopen(req, timeout=args.timeout) as resp:
            response_body = resp.read().decode("utf-8")
            result = json.loads(response_body)
            print(json.dumps(result, indent=2))
            return 0
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8") if exc.fp else ""
        print(f"Score request failed: {exc.code} {exc.reason}", file=sys.stderr)
        if error_body:
            print(error_body, file=sys.stderr)
        return 1
    except error.URLError as exc:
        print(f"Score request failed: {exc}", file=sys.stderr)
        return 1


def cmd_analyze(args: argparse.Namespace) -> int:
    """Get detailed analysis with recommendations"""
    url = normalize_url(args.base_url, "/api/analyze/")
    
    payload = {
        "api_url": args.api_url,
        "endpoints": args.endpoints.split(",") if args.endpoints else [],
        "documentation": args.documentation,
        "response_format": args.response_format or "json",
        "authentication": args.authentication,
        "error_handling": args.error_handling,
        "versioning": args.versioning,
    }
    
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers=headers, method="POST")
    
    try:
        with request.urlopen(req, timeout=args.timeout) as resp:
            response_body = resp.read().decode("utf-8")
            result = json.loads(response_body)
            print(json.dumps(result, indent=2))
            return 0
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8") if exc.fp else ""
        print(f"Analysis failed: {exc.code} {exc.reason}", file=sys.stderr)
        if error_body:
            print(error_body, file=sys.stderr)
        return 1
    except error.URLError as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="protocol80",
        description="CLI for interacting with Protocol 80 API and Django project.",
    )

    parser.add_argument(
        "--base-url",
        default=DEFAULT_API_URL,
        help="API base URL (default: %(default)s or PROTOCOL80_API_URL env var)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="HTTP timeout in seconds (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    health_parser = subparsers.add_parser("health", help="Check API health endpoint")
    health_parser.set_defaults(func=cmd_health)

    request_parser = subparsers.add_parser("request", help="Send HTTP request to API")
    request_parser.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"], help="HTTP method")
    request_parser.add_argument("path", help="API path, e.g. /health/")
    request_parser.add_argument("--data", help="JSON request body as string")
    request_parser.add_argument("--token", help="Bearer token for Authorization header")
    request_parser.set_defaults(func=cmd_request)

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate API usability (full report)")
    evaluate_parser.add_argument("api_url", help="URL of the API to evaluate")
    evaluate_parser.add_argument("--endpoints", help="Comma-separated list of endpoints")
    evaluate_parser.add_argument("--documentation", action="store_true", help="API has documentation")
    evaluate_parser.add_argument("--response-format", choices=["json", "xml", "other"], help="Response format")
    evaluate_parser.add_argument("--authentication", action="store_true", help="API has authentication")
    evaluate_parser.add_argument("--error-handling", action="store_true", help="API has error handling")
    evaluate_parser.add_argument("--versioning", action="store_true", help="API has versioning")
    evaluate_parser.set_defaults(func=cmd_evaluate)

    score_parser = subparsers.add_parser("score", help="Get quick usability score")
    score_parser.add_argument("api_url", help="URL of the API to score")
    score_parser.add_argument("--endpoints", help="Comma-separated list of endpoints")
    score_parser.add_argument("--documentation", action="store_true", help="API has documentation")
    score_parser.add_argument("--response-format", choices=["json", "xml", "other"], help="Response format")
    score_parser.add_argument("--authentication", action="store_true", help="API has authentication")
    score_parser.add_argument("--error-handling", action="store_true", help="API has error handling")
    score_parser.add_argument("--versioning", action="store_true", help="API has versioning")
    score_parser.set_defaults(func=cmd_score)

    analyze_parser = subparsers.add_parser("analyze", help="Get detailed analysis with recommendations")
    analyze_parser.add_argument("api_url", help="URL of the API to analyze")
    analyze_parser.add_argument("--endpoints", help="Comma-separated list of endpoints")
    analyze_parser.add_argument("--documentation", action="store_true", help="API has documentation")
    analyze_parser.add_argument("--response-format", choices=["json", "xml", "other"], help="Response format")
    analyze_parser.add_argument("--authentication", action="store_true", help="API has authentication")
    analyze_parser.add_argument("--error-handling", action="store_true", help="API has error handling")
    analyze_parser.add_argument("--versioning", action="store_true", help="API has versioning")
    analyze_parser.set_defaults(func=cmd_analyze)

    manage_parser = subparsers.add_parser("manage", help="Run Django manage.py commands")
    manage_parser.add_argument("manage_args", nargs=argparse.REMAINDER, help="Arguments passed to manage.py")
    manage_parser.set_defaults(func=cmd_manage)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
