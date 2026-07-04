"""Typed application errors. Services raise these; the API layer maps them to responses."""
from rest_framework import status
from rest_framework.exceptions import APIException


class AppError(APIException):
  """Base for all orchestrator service errors. Carries an HTTP status and a code."""

  status_code = status.HTTP_400_BAD_REQUEST
  default_detail = "Application error."
  default_code = "app_error"


class NotFoundError(AppError):
  status_code = status.HTTP_404_NOT_FOUND
  default_detail = "Resource not found."
  default_code = "not_found"


class UpstreamError(AppError):
  """A dependency (GitHub, Forgejo) returned an unexpected response."""

  status_code = status.HTTP_502_BAD_GATEWAY
  default_detail = "Upstream service error."
  default_code = "upstream_error"


class GuardrailError(AppError):
  """A destructive or unsafe action was blocked by a guardrail."""

  status_code = status.HTTP_409_CONFLICT
  default_detail = "Action blocked by guardrail."
  default_code = "guardrail_blocked"
