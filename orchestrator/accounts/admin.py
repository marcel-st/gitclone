from django.contrib import admin

from .models import GithubAccount


@admin.register(GithubAccount)
class GithubAccountAdmin(admin.ModelAdmin):
  list_display = ["login", "is_self", "enabled", "created_at"]
  list_filter = ["is_self", "enabled"]
  # Never surface the encrypted PAT in the admin.
  exclude = ["pat_encrypted"]
