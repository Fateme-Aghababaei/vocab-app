from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WordViewSet, StatsView

router = DefaultRouter()
router.register(r"words", WordViewSet, basename="word")

urlpatterns = [
    path("stats/", StatsView.as_view(), name="stats"),
    path("", include(router.urls)),
]
