from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, StoreViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('stores', StoreViewSet, basename='store')

urlpatterns = [
    path('', include(router.urls)),
]