from rest_framework.routers import DefaultRouter

from .views import MirroredRepoViewSet, TrackedTargetViewSet

router = DefaultRouter()
router.register("targets", TrackedTargetViewSet, basename="tracked-target")
router.register("repos", MirroredRepoViewSet, basename="mirrored-repo")

urlpatterns = router.urls
