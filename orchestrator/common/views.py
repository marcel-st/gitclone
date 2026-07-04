"""Cross-cutting endpoints."""
from django.http import HttpRequest, JsonResponse


def healthz(request: HttpRequest) -> JsonResponse:
  """Liveness probe used by the container healthcheck."""
  return JsonResponse({"status": "ok"})
