import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["POST"])
def evaluate(request):
    """
    Evaluate API usability.
    Accept API details and pass to backend ruling system.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    api_url = data.get("api_url")
    if not api_url:
        return JsonResponse({"error": "api_url is required"}, status=400)

    # TODO: Integrate with backend ruling system
    return JsonResponse({
        "service": "protocol-80-api",
        "api_url": api_url,
        "status": "received",
        "data": data,
        "message": "Evaluation data received. Integrate with your backend scoring service."
    })


@csrf_exempt
@require_http_methods(["POST"])
def score(request):
    """
    Get usability score for an API.
    IntegratesWith backend ruling system.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    # TODO: Integrate with backend ruling system
    return JsonResponse({
        "service": "protocol-80-api",
        "status": "received",
        "data": data,
        "message": "Score request received. Integrate with your backend scoring service."
    })


@csrf_exempt
@require_http_methods(["POST"])
def analyze(request):
    """
    Detailed analysis for an API.
    Integrates with backend ruling system.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    api_url = data.get("api_url", "unknown")

    # TODO: Integrate with backend ruling system
    return JsonResponse({
        "service": "protocol-80-api",
        "api_url": api_url,
        "status": "received",
        "data": data,
        "message": "Analysis request received. Integrate with your backend scoring service."
    })


