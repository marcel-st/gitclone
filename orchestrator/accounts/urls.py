from rest_framework.routers import DefaultRouter

from .views import GithubAccountViewSet

router = DefaultRouter()
router.register("", GithubAccountViewSet, basename="github-account")

urlpatterns = router.urls
