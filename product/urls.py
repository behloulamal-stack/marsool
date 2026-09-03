from django.urls import path
from .views import (
    MyMenuListCreateView, MyMenuDetailView,
    MyOptionGroupListCreateView, MyOptionGroupDetailView,
    MyOptionCreateView, MyOptionDetailView,
    MyProductCreateView, MyProductDetailView,
    StoreMenusPublicView,
)

urlpatterns = [
    # ─── لوحة التاجر (خاص) ───
    path('my/menus/', MyMenuListCreateView.as_view(), name='my-menus'),
    path('my/menus/<int:pk>/', MyMenuDetailView.as_view(), name='my-menu-detail'),

    path('my/option-groups/', MyOptionGroupListCreateView.as_view(), name='my-option-groups'),
    path('my/option-groups/<int:pk>/', MyOptionGroupDetailView.as_view(), name='my-option-group-detail'),

    path('my/options/', MyOptionCreateView.as_view(), name='my-options'),
    path('my/options/<int:pk>/', MyOptionDetailView.as_view(), name='my-option-detail'),

    path('my/products/', MyProductCreateView.as_view(), name='my-products'),
    path('my/products/<int:pk>/', MyProductDetailView.as_view(), name='my-product-detail'),

    # ─── عام ───
    path('stores/<int:store_id>/menus/', StoreMenusPublicView.as_view(), name='store-menus-public'),
]