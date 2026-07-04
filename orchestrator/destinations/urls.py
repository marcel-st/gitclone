from rest_framework.routers import DefaultRouter

from .views import AuditLogViewSet, PushDestinationViewSet, PushMirrorLinkViewSet

router = DefaultRouter()
router.register("destinations", PushDestinationViewSet, basename="push-destination")
router.register("links", PushMirrorLinkViewSet, basename="push-link")
router.register("audit", AuditLogViewSet, basename="audit-log")

urlpatterns = router.urls
