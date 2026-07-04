"""DRF views for managing GitHub accounts. Admin-only (see REST_FRAMEWORK settings)."""
from rest_framework import viewsets

from .models import GithubAccount
from .serializers import GithubAccountSerializer


class GithubAccountViewSet(viewsets.ModelViewSet):
  serializer_class = GithubAccountSerializer

  def get_queryset(self):
    return GithubAccount.objects.filter(deleted_at__isnull=True)
