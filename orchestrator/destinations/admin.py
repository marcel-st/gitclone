from django.contrib import admin

from .models import AuditLog, PushDestination, PushMirrorLink


@admin.register(PushDestination)
class PushDestinationAdmin(admin.ModelAdmin):
  list_display = ["name", "type", "remote_url", "enabled"]
  list_filter = ["type", "enabled"]
  # Never surface the encrypted write token.
  exclude = ["write_token_encrypted"]


@admin.register(PushMirrorLink)
class PushMirrorLinkAdmin(admin.ModelAdmin):
  list_display = ["__str__", "require_confirmation", "last_pushed_at"]
  list_filter = ["require_confirmation"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
  list_display = ["created_at", "actor", "action", "target"]
  list_filter = ["action"]
  search_fields = ["target", "actor"]
  readonly_fields = ["actor", "action", "target", "detail", "created_at"]

  def has_add_permission(self, request) -> bool:
    return False  # audit log is append-only via services

  def has_change_permission(self, request, obj=None) -> bool:
    return False
