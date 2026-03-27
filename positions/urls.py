from django.urls import path, include
from rest_framework.routers import DefaultRouter
from positions.views.designation import DesignationViewSet
from positions.views.level import LevelViewSet


router = DefaultRouter()
router.register(r'designations', DesignationViewSet, basename='designation')
router.register(r'levels', LevelViewSet, basename='level')

urlpatterns = [
    path('v1/positions/', include(router.urls)),
]