"""Abstract base model applying the project's table conventions."""
import uuid

from django.db import models


class TimeStampedUUIDModel(models.Model):
  """UUID primary key + created/updated/deleted timestamps. Soft-delete via deleted_at."""

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  deleted_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    abstract = True

  @property
  def is_deleted(self) -> bool:
    return self.deleted_at is not None
