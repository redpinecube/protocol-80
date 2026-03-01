import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from . import gemini 

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

    # gemini_response = gemini.tryAPI(api_url) 
    
    result = gemini.evaluate_api(api_url)

    status_code = result.get("status_code", 500)

    if status_code == 401:
        return JsonResponse({
            "service": "ratemyapi",
            "error": "UNAUTHORIZED",
            "message": "Private API but a private key was not provided"
        }, status=401)
    
    if status_code == 422:
        return JsonResponse({
            "service": "ratemyapi",
            "error": "UNPROCESSABLE_ENTITY",
            "message": "The link could not be resolved or is unresponsive."
        }, status=422)
    
    if status_code == 503:
        return JsonResponse({
            "service": "ratemyapi",
            "error": "SERVICE_UNAVAILABLE",
            "message": "AI Auditor is down. Please try again later."
        }, status=503)
    
        # 2. Handle Success
    if status_code == 200:
        return JsonResponse({
            "service": "ratemyapi",
            "object": "evaluation",
            "api_url": api_url,
            "SCORE": result.get("SCORE"),
            "status": "completed"
        }, status=200)

    return JsonResponse({"error": "INTERNAL_ERROR", "message": "An unexpected error occurred."}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze(request):
    """
    Detailed analysis for an API.
    Provides deep insights and a remediation plan for agentic readiness.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "INVALID_JSON", "message": "Invalid JSON payload"}, status=400)

    api_url = data.get("api_url")
    if not api_url:
        return JsonResponse({"error": "PARAMETER_MISSING", "message": "api_url is required"}, status=400)

    # 1. Integration with Gemini Backend
    # We call a specific 'analyze_api' function that returns deeper insights
    try:
        # Pass the whole data dict so Gemini has context (auth_type, environment, etc.)
        result = gemini.analyze_api(api_url) 
    except Exception as e:
        # Fallback if the gemini module itself crashes
        result = {"status_code": 503}

    status_code = result.get("status_code", 500)

    # 2. Consistent Error Handling
    if status_code == 401:
        return JsonResponse({
            "service": "ratemyapi",
            "error": "UNAUTHORIZED",
            "message": "Authentication failed for the target API documentation."
        }, status=401)
    
    if status_code == 422:
        return JsonResponse({
            "service": "ratemyapi",
            "error": "UNPROCESSABLE_ENTITY",
            "message": "The documentation at the provided link is unreadable or malformed."
        }, status=422)
    
    if status_code == 503:
        return JsonResponse({
            "service": "ratemyapi",
            "error": "SERVICE_UNAVAILABLE",
            "message": "The Analysis Engine is currently overloaded. Please try again."
        }, status=503)

    # 3. Handle Success: Return Detailed Insights
    if status_code == 200:
        return JsonResponse({
            "service": "ratemyapi",
            "object": "analysis_report",
            "api_url": api_url,
            "score": result.get("SCORE"),
            "findings": result.get("findings", []),           # List of issues
            "remediation_plan": result.get("remediation"),     # Step-by-step fix
            "agent_friction": result.get("friction_points"),   # Why AI struggles with it
            "status": "completed"
        }, status=200)

    return JsonResponse({"error": "INTERNAL_ERROR", "message": "An unexpected analysis error occurred."}, status=500)
