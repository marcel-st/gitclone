from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from . import services
from .models import AuditLog, PushDestination, PushMirrorLink
from .serializers import (
  AuditLogSerializer,
  PushDestinationSerializer,
  PushMirrorLinkSerializer,
)


class PushDestinationViewSet(viewsets.ModelViewSet):
  serializer_class = PushDestinationSerializer

  def get_queryset(self):
    return PushDestination.objects.filter(deleted_at__isnull=True)


class PushMirrorLinkViewSet(viewsets.ModelViewSet):
  serializer_class = PushMirrorLinkSerializer

  def get_queryset(self):
    return PushMirrorLink.objects.filter(deleted_at__isnull=True)

  @action(detail=True, methods=["post"])
  def push(self, request: Request, pk: str | None = None) -> Response:
    """Trigger a mirror-out. Body: {"confirmed": true}. Force-updates the remote."""
    link = self.get_object()
    confirmed = bool(request.data.get("confirmed", False))
    services.push_now(link, actor=request.user.get_username(), confirmed=confirmed)
    return Response({"status": "pushed", "link": str(link)})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = AuditLogSerializer
  queryset = AuditLog.objects.all()
