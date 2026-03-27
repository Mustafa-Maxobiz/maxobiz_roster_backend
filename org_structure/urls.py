# org_structure/urls.py
from rest_framework import routers
from django.urls import path, include
from org_structure.views.department import DepartmentViewSet
from org_structure.views.group import GroupViewSet
from org_structure.views.organization import OrganizationViewSet

router = routers.DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'organizations', OrganizationViewSet, basename='organization')

urlpatterns = [
    path('', include(router.urls)),
]