#!/usr/bin/env python3
import argparse
import json
import os
import re
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


def validate_http_url(value: str) -> str:
    parsed = parse.urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise argparse.ArgumentTypeError(
            "Invalid URL for --body. Use a full URL like https://example.com/app.json"
        )
    return value


def validate_timeout_seconds(value: str) -> int:
    try:
        timeout = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--timeout must be an integer") from exc

    if timeout <= 0:
        raise argparse.ArgumentTypeError("--timeout must be greater than 0")
    if timeout > 120:
        raise argparse.ArgumentTypeError("--timeout must be 120 seconds or less")
    return timeout


def parse_endpoints(raw_endpoints: str | None) -> list[str]:
    if not raw_endpoints:
        return []

    endpoints = [item.strip() for item in raw_endpoints.split(",") if item.strip()]
    invalid = [item for item in endpoints if not item.startswith("/")]
    if invalid:
        bad_values = ", ".join(invalid)
        raise ValueError(
            f"Invalid endpoint format: {bad_values}. Endpoints must start with '/'."
        )
    return endpoints


def validate_private_api_key(api_key: str | None) -> str | None:
    if api_key is None:
        return None
    if len(api_key) < 8:
        raise ValueError("--private-api-key is too short. Use at least 8 characters.")
    if re.search(r"\s", api_key):
        raise ValueError("--private-api-key cannot contain spaces.")
    return api_key


def validate_auth_token(auth_token: str | None) -> str | None:
    if auth_token is None:
        return None
    if len(auth_token) < 8:
        raise ValueError("--auth-token is too short. Use at least 8 characters.")
    if re.search(r"\s", auth_token):
        raise ValueError("--auth-token cannot contain spaces.")
    return auth_token


def validate_auth_inputs(
    auth_type: str,
    private_api_key: str | None,
    auth_token: str | None,
) -> None:
    if auth_type == "none":
        if private_api_key or auth_token:
            raise ValueError(
                "auth_type is 'none', so do not pass --private-api-key or --auth-token."
            )
        return

    if auth_type == "api_key" and not private_api_key:
        raise ValueError("auth_type 'api_key' requires --private-api-key.")

    if auth_type in {"bearer", "basic"} and not auth_token:
        raise ValueError(f"auth_type '{auth_type}' requires --auth-token.")


def validate_environment_inputs(args: argparse.Namespace) -> None:
    if args.environment == "prod" and args.do_simulation and not args.allow_prod_simulation:
        raise ValueError(
            "Simulation against prod is blocked. Use --allow-prod-simulation to confirm."
        )


def print_backend_error(prefix: str, error_body: str) -> None:
    if not error_body:
        return

    try:
        payload = json.loads(error_body)
    except json.JSONDecodeError:
        print(error_body, file=sys.stderr)
        return

    if isinstance(payload, dict):
        code = payload.get("code")
        field = payload.get("field")
        message = payload.get("message") or payload.get("error")
        hint = payload.get("hint")

        if code or field or message or hint:
            if code:
                print(f"{prefix} code: {code}", file=sys.stderr)
            if field:
                print(f"{prefix} field: {field}", file=sys.stderr)
            if message:
                print(f"{prefix} message: {message}", file=sys.stderr)
            if hint:
                print(f"{prefix} hint: {hint}", file=sys.stderr)
            return

    print(json.dumps(payload, indent=2), file=sys.stderr)


def build_evaluation_payload(args: argparse.Namespace) -> dict:
    try:
        endpoints = parse_endpoints(args.endpoints)
        private_api_key = validate_private_api_key(args.private_api_key)
        auth_token = validate_auth_token(args.auth_token)
        validate_auth_inputs(args.auth_type, private_api_key, auth_token)
        validate_environment_inputs(args)
    except ValueError as exc:
        print(f"Input validation error: {exc}", file=sys.stderr)
        raise

    return {
        "body": args.body,
        "private_api_key": private_api_key,
        "auth_type": args.auth_type,
        "auth_token": auth_token,
        "docs_format": args.docs_format,
        "environment": args.environment,
        "do_simulation": args.do_simulation,
        "api_url": args.body,
        "endpoints": endpoints,
        "documentation": args.documentation,
        "response_format": args.response_format or "json",
        "authentication": args.authentication,
        "error_handling": args.error_handling,
        "versioning": args.versioning,
    }


def post_json(url: str, payload: dict, timeout: int) -> dict:
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers=headers, method="POST")
    with request.urlopen(req, timeout=timeout) as resp:
        response_body = resp.read().decode("utf-8")
        return json.loads(response_body)


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
        print_backend_error("Request", error_body)
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
    try:
        payload = build_evaluation_payload(args)
    except ValueError:
        return 2
    
    try:
        result = post_json(url, payload, args.timeout)
        print(json.dumps(result, indent=2))
        return 0
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8") if exc.fp else ""
        print(f"Evaluation failed: {exc.code} {exc.reason}", file=sys.stderr)
        print_backend_error("Evaluation", error_body)
        return 1
    except json.JSONDecodeError:
        print("Evaluation failed: backend response is not valid JSON", file=sys.stderr)
        return 1
    except error.URLError as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        return 1


def cmd_score(args: argparse.Namespace) -> int:
    """Get usability score for an API"""
    url = normalize_url(args.base_url, "/api/score/")
    try:
        payload = build_evaluation_payload(args)
    except ValueError:
        return 2
    
    try:
        result = post_json(url, payload, args.timeout)
        print(json.dumps(result, indent=2))
        return 0
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8") if exc.fp else ""
        print(f"Score request failed: {exc.code} {exc.reason}", file=sys.stderr)
        print_backend_error("Score", error_body)
        return 1
    except json.JSONDecodeError:
        print("Score request failed: backend response is not valid JSON", file=sys.stderr)
        return 1
    except error.URLError as exc:
        print(f"Score request failed: {exc}", file=sys.stderr)
        return 1


def cmd_analyze(args: argparse.Namespace) -> int:
    """Get detailed analysis with recommendations"""
    url = normalize_url(args.base_url, "/api/analyze/")
    try:
        payload = build_evaluation_payload(args)
    except ValueError:
        return 2
    
    try:
        result = post_json(url, payload, args.timeout)
        print(json.dumps(result, indent=2))
        return 0
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8") if exc.fp else ""
        print(f"Analysis failed: {exc.code} {exc.reason}", file=sys.stderr)
        print_backend_error("Analysis", error_body)
        return 1
    except json.JSONDecodeError:
        print("Analysis failed: backend response is not valid JSON", file=sys.stderr)
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
        type=validate_timeout_seconds,
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
    evaluate_parser.add_argument("--body", required=True, type=validate_http_url, help="Link to API docs/spec, e.g. https://example.com/openapi.json")
    evaluate_parser.add_argument("--private-api-key", default=os.environ.get("PROTOCOL80_PRIVATE_API_KEY"), help="Private API key if required (optional)")
    evaluate_parser.add_argument("--auth-type", choices=["none", "bearer", "basic", "api_key"], default="none", help="Authentication strategy for target API")
    evaluate_parser.add_argument("--auth-token", default=os.environ.get("PROTOCOL80_AUTH_TOKEN"), help="Auth token for bearer/basic auth (optional)")
    evaluate_parser.add_argument("--docs-format", choices=["openapi", "swagger", "postman", "other"], default="openapi", help="Documentation format for --body")
    evaluate_parser.add_argument("--environment", choices=["dev", "staging", "prod"], default="dev", help="Target API environment")
    evaluate_parser.add_argument("--do-simulation", action="store_true", default=False, help="Run simulation checks (default: false)")
    evaluate_parser.add_argument("--allow-prod-simulation", action="store_true", default=False, help="Allow simulation when environment=prod")
    evaluate_parser.add_argument("--endpoints", help="Comma-separated list of endpoints")
    evaluate_parser.add_argument("--documentation", action="store_true", help="API has documentation")
    evaluate_parser.add_argument("--response-format", choices=["json", "xml", "other"], help="Response format")
    evaluate_parser.add_argument("--authentication", action="store_true", help="API has authentication")
    evaluate_parser.add_argument("--error-handling", action="store_true", help="API has error handling")
    evaluate_parser.add_argument("--versioning", action="store_true", help="API has versioning")
    evaluate_parser.set_defaults(func=cmd_evaluate)

    score_parser = subparsers.add_parser("score", help="Get quick usability score")
    score_parser.add_argument("--body", required=True, type=validate_http_url, help="Link to API docs/spec, e.g. https://example.com/openapi.json")
    score_parser.add_argument("--private-api-key", default=os.environ.get("PROTOCOL80_PRIVATE_API_KEY"), help="Private API key if required (optional)")
    score_parser.add_argument("--auth-type", choices=["none", "bearer", "basic", "api_key"], default="none", help="Authentication strategy for target API")
    score_parser.add_argument("--auth-token", default=os.environ.get("PROTOCOL80_AUTH_TOKEN"), help="Auth token for bearer/basic auth (optional)")
    score_parser.add_argument("--docs-format", choices=["openapi", "swagger", "postman", "other"], default="openapi", help="Documentation format for --body")
    score_parser.add_argument("--environment", choices=["dev", "staging", "prod"], default="dev", help="Target API environment")
    score_parser.add_argument("--do-simulation", action="store_true", default=False, help="Run simulation checks (default: false)")
    score_parser.add_argument("--allow-prod-simulation", action="store_true", default=False, help="Allow simulation when environment=prod")
    score_parser.add_argument("--endpoints", help="Comma-separated list of endpoints")
    score_parser.add_argument("--documentation", action="store_true", help="API has documentation")
    score_parser.add_argument("--response-format", choices=["json", "xml", "other"], help="Response format")
    score_parser.add_argument("--authentication", action="store_true", help="API has authentication")
    score_parser.add_argument("--error-handling", action="store_true", help="API has error handling")
    score_parser.add_argument("--versioning", action="store_true", help="API has versioning")
    score_parser.set_defaults(func=cmd_score)

    analyze_parser = subparsers.add_parser("analyze", help="Get detailed analysis with recommendations")
    analyze_parser.add_argument("--body", required=True, type=validate_http_url, help="Link to API docs/spec, e.g. https://example.com/openapi.json")
    analyze_parser.add_argument("--private-api-key", default=os.environ.get("PROTOCOL80_PRIVATE_API_KEY"), help="Private API key if required (optional)")
    analyze_parser.add_argument("--auth-type", choices=["none", "bearer", "basic", "api_key"], default="none", help="Authentication strategy for target API")
    analyze_parser.add_argument("--auth-token", default=os.environ.get("PROTOCOL80_AUTH_TOKEN"), help="Auth token for bearer/basic auth (optional)")
    analyze_parser.add_argument("--docs-format", choices=["openapi", "swagger", "postman", "other"], default="openapi", help="Documentation format for --body")
    analyze_parser.add_argument("--environment", choices=["dev", "staging", "prod"], default="dev", help="Target API environment")
    analyze_parser.add_argument("--do-simulation", action="store_true", default=False, help="Run simulation checks (default: false)")
    analyze_parser.add_argument("--allow-prod-simulation", action="store_true", default=False, help="Allow simulation when environment=prod")
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
