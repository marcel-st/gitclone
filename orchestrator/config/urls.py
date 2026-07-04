"""Root URL routing. Dashboard under /admin/, API under /orchestrator-api/."""
from django.contrib import admin
from django.urls import include, path

from common.views import healthz

urlpatterns = [
  path("healthz/", healthz, name="healthz"),
  path("admin/", admin.site.urls),
  path("orchestrator-api/accounts/", include("accounts.urls")),
  path("orchestrator-api/mirrors/", include("mirrors.urls")),
  path("orchestrator-api/destinations/", include("destinations.urls")),
]
