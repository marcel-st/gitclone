from rest_framework import serializers

from .models import AuditLog, PushDestination, PushMirrorLink


class PushDestinationSerializer(serializers.ModelSerializer):
  # Accepted on write, never returned.
  write_token = serializers.CharField(write_only=True, source="write_token_encrypted")

  class Meta:
    model = PushDestination
    fields = [
      "id", "name", "type", "remote_url", "remote_username",
      "write_token", "enabled", "created_at", "updated_at",
    ]
    read_only_fields = ["id", "created_at", "updated_at"]


class PushMirrorLinkSerializer(serializers.ModelSerializer):
  class Meta:
    model = PushMirrorLink
    fields = [
      "id", "repo", "destination", "require_confirmation",
      "last_pushed_at", "created_at",
    ]
    read_only_fields = ["id", "last_pushed_at", "created_at"]


class AuditLogSerializer(serializers.ModelSerializer):
  class Meta:
    model = AuditLog
    fields = ["id", "actor", "action", "target", "detail", "created_at"]
    read_only_fields = fields
