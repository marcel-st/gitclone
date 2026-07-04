from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from . import services
from .models import MirroredRepo, TrackedTarget
from .serializers import MirroredRepoSerializer, TrackedTargetSerializer


class TrackedTargetViewSet(viewsets.ModelViewSet):
  serializer_class = TrackedTargetSerializer

  def get_queryset(self):
    return TrackedTarget.objects.filter(deleted_at__isnull=True)

  @action(detail=False, methods=["post"])
  def discover(self, request: Request) -> Response:
    """Manually trigger a discovery + mirror-in run across all enabled targets."""
    summary = services.run_discovery()
    return Response(summary)


class MirroredRepoViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = MirroredRepoSerializer

  def get_queryset(self):
    return MirroredRepo.objects.filter(deleted_at__isnull=True)
