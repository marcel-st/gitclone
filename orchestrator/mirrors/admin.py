from django.contrib import admin

from .models import MirroredRepo, TrackedTarget


@admin.register(TrackedTarget)
class TrackedTargetAdmin(admin.ModelAdmin):
  list_display = ["__str__", "kind", "account", "enabled"]
  list_filter = ["kind", "enabled"]


@admin.register(MirroredRepo)
class MirroredRepoAdmin(admin.ModelAdmin):
  list_display = ["source_full_name", "last_sync_status", "is_private", "size_bytes", "last_sync_at"]
  list_filter = ["last_sync_status", "is_private"]
  search_fields = ["source_full_name"]
  readonly_fields = ["forgejo_repo_id"]
