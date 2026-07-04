"""Symmetric-encryption model field for secrets stored at rest (PATs, push tokens)."""
from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models


def _fernet() -> Fernet:
  key = settings.FIELD_ENCRYPTION_KEY
  if not key:
    raise RuntimeError("FIELD_ENCRYPTION_KEY is not set; cannot encrypt secrets.")
  return Fernet(key.encode() if isinstance(key, str) else key)


class EncryptedTextField(models.TextField):
  """Stores its value Fernet-encrypted. Plaintext is only ever in memory."""

  def get_prep_value(self, value: str | None) -> str | None:
    if value is None or value == "":
      return value
    return _fernet().encrypt(value.encode()).decode()

  def from_db_value(self, value: str | None, expression, connection) -> str | None:
    if value is None or value == "":
      return value
    return _fernet().decrypt(value.encode()).decode()
