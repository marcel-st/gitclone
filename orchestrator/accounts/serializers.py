"""Input/output serialization for GithubAccount. The PAT is write-only."""
from rest_framework import serializers

from .models import GithubAccount


class GithubAccountSerializer(serializers.ModelSerializer):
  # Accepted on write, never returned.
  pat = serializers.CharField(write_only=True, source="pat_encrypted")

  class Meta:
    model = GithubAccount
    fields = ["id", "login", "pat", "is_self", "enabled", "created_at", "updated_at"]
    read_only_fields = ["id", "created_at", "updated_at"]
