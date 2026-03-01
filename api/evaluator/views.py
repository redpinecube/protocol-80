import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from . import gemini


@csrf_exempt
@require_http_methods(["POST"])
def evaluate(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    api_url = data.get("api_url")
    if not api_url:
        return JsonResponse({"error": "api_url is required"}, status=400)

    # Trigger the AI evaluation
    result = gemini.evaluate_api(api_url)
    status_code = result.get("status_code", 500)

    # --- Error Handling ---
    if status_code == 401:
        return JsonResponse(
            {
                "service": "ratemyapi",
                "error": "UNAUTHORIZED",
                "message": "Private API but a private key was not provided",
            },
            status=401,
        )

    if status_code == 422:
        return JsonResponse(
            {
                "service": "ratemyapi",
                "error": "UNPROCESSABLE_ENTITY",
                "message": "The link could not be resolved or is unresponsive.",
            },
            status=422,
        )

    if status_code == 503:
        return JsonResponse(
            {
                "service": "ratemyapi",
                "error": "SERVICE_UNAVAILABLE",
                "message": "AI Auditor is down. Please try again later.",
            },
            status=503,
        )

    if status_code == 200:
        return JsonResponse(
            {
                "service": "ratemyapi",
                "object": "evaluation",
                "api_url": api_url,
                "score": result.get("SCORE"),
                "status": "completed",
            },
            status=200,
        )

    return JsonResponse(
        {"error": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
        status=500,
    )


@csrf_exempt
@require_http_methods(["POST"])
def analyze(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "INVALID_JSON", "message": "Invalid JSON payload"}, status=400
        )

    api_url = data.get("api_url")
    if not api_url:
        return JsonResponse(
            {"error": "PARAMETER_MISSING", "message": "api_url is required"}, status=400
        )

    try:
        result = gemini.analyze_api(api_url)
    except Exception:
        result = {"status_code": 503}

    status_code = result.get("status_code", 500)

    if status_code == 401:
        return JsonResponse(
            {
                "service": "ratemyapi",
                "error": "UNAUTHORIZED",
                "message": "Authentication failed for the target API documentation.",
            },
            status=401,
        )

    if status_code == 422:
        return JsonResponse(
            {
                "service": "ratemyapi",
                "error": "UNPROCESSABLE_ENTITY",
                "message": "The documentation at the provided link is unreadable or malformed.",
            },
            status=422,
        )

    if status_code == 503:
        return JsonResponse(
            {
                "service": "ratemyapi",
                "error": "SERVICE_UNAVAILABLE",
                "message": "The Analysis Engine is currently overloaded.",
            },
            status=503,
        )

    if status_code == 200:
        return JsonResponse(
            {
                "service": "ratemyapi",
                "object": "analysis_report",
                "api_url": api_url,
                "score": result.get("SCORE"),
                "findings": result.get("findings", []),
                "remediation_plan": result.get("remediation"),
                "agent_friction": result.get("friction_points"),
                "status": "completed",
            },
            status=200,
        )

    return JsonResponse(
        {
            "error": "INTERNAL_ERROR",
            "message": "An unexpected analysis error occurred.",
        },
        status=500,
    )
