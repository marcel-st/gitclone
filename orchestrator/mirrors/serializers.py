from rest_framework import serializers

from .models import MirroredRepo, TrackedTarget


class TrackedTargetSerializer(serializers.ModelSerializer):
  class Meta:
    model = TrackedTarget
    fields = [
      "id", "account", "kind", "github_login", "repo_full_name",
      "enabled", "created_at", "updated_at",
    ]
    read_only_fields = ["id", "created_at", "updated_at"]

  def validate(self, attrs: dict) -> dict:
    kind = attrs.get("kind")
    if kind == TrackedTarget.Kind.USER_ALL and not attrs.get("github_login"):
      raise serializers.ValidationError("github_login is required for user_all targets.")
    if kind == TrackedTarget.Kind.REPO and not attrs.get("repo_full_name"):
      raise serializers.ValidationError("repo_full_name is required for repo targets.")
    return attrs


class MirroredRepoSerializer(serializers.ModelSerializer):
  class Meta:
    model = MirroredRepo
    fields = [
      "id", "source_full_name", "forgejo_owner", "forgejo_repo_name",
      "is_private", "size_bytes", "last_sync_at", "last_sync_status",
      "last_error", "created_at",
    ]
    read_only_fields = fields
