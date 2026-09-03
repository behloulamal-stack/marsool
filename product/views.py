from rest_framework import generics, permissions
from .models import Menu, Product, OptionGroup, Option
from .serializers import (
    MenuWriteSerializer, MenuReadSerializer,
    ProductWriteSerializer, ProductSerializer,
    OptionGroupWriteSerializer, OptionGroupSerializer,
    OptionWriteSerializer,
)
from store.permissions import IsApprovedStoreOwner


# ═══════════════════════════════════════════════════════════════
# MENUS (الفئات)
# ═══════════════════════════════════════════════════════════════

class MyMenuListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsApprovedStoreOwner]

    def get_serializer_class(self):
        return MenuWriteSerializer if self.request.method == 'POST' else MenuReadSerializer

    def get_queryset(self):
        return Menu.objects.filter(
            store=self.request.user.store
        ).prefetch_related('products__options__option_group')

    def perform_create(self, serializer):
        serializer.save(store=self.request.user.store)

    def get_serializer_context(self):
        return {'request': self.request}


class MyMenuDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsApprovedStoreOwner]

    def get_serializer_class(self):
        return MenuReadSerializer if self.request.method == 'GET' else MenuWriteSerializer

    def get_queryset(self):
        # الفلترة بـ store=request.user.store تمنع أي تاجر من الوصول لقائمة تاجر آخر
        # حتى لو خمّن الـ id — يرجع 404 (وليس 403)، وهذا الأصح أمنياً
        return Menu.objects.filter(
            store=self.request.user.store
        ).prefetch_related('products__options__option_group')


# ═══════════════════════════════════════════════════════════════
# OPTION GROUPS (مجموعات الإضافات)
# ═══════════════════════════════════════════════════════════════

class MyOptionGroupListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsApprovedStoreOwner]

    def get_serializer_class(self):
        return OptionGroupWriteSerializer if self.request.method == 'POST' else OptionGroupSerializer

    def get_queryset(self):
        return OptionGroup.objects.filter(
            store=self.request.user.store
        ).prefetch_related('options')

    def perform_create(self, serializer):
        serializer.save(store=self.request.user.store)


class MyOptionGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsApprovedStoreOwner]

    def get_serializer_class(self):
        return OptionGroupSerializer if self.request.method == 'GET' else OptionGroupWriteSerializer

    def get_queryset(self):
        return OptionGroup.objects.filter(
            store=self.request.user.store
        ).prefetch_related('options')


# ═══════════════════════════════════════════════════════════════
# OPTIONS (خيارات فردية داخل مجموعة)
# ═══════════════════════════════════════════════════════════════

class MyOptionCreateView(generics.CreateAPIView):
    """التاجر يضيف خيار جوه مجموعة تخصه (مثلاً 'جبنة' جوه 'الإضافات')"""
    serializer_class   = OptionWriteSerializer
    permission_classes = [permissions.IsAuthenticated, IsApprovedStoreOwner]

    def get_serializer_context(self):
        return {'request': self.request}


class MyOptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = OptionWriteSerializer
    permission_classes = [permissions.IsAuthenticated, IsApprovedStoreOwner]

    def get_queryset(self):
        return Option.objects.filter(option_group__store=self.request.user.store)

    def get_serializer_context(self):
        return {'request': self.request}


# ═══════════════════════════════════════════════════════════════
# PRODUCTS (المنتجات)
# ═══════════════════════════════════════════════════════════════

class MyProductCreateView(generics.CreateAPIView):
    serializer_class   = ProductWriteSerializer
    permission_classes = [permissions.IsAuthenticated, IsApprovedStoreOwner]

    def get_serializer_context(self):
        return {'request': self.request}


class MyProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsApprovedStoreOwner]

    def get_serializer_class(self):
        return ProductSerializer if self.request.method == 'GET' else ProductWriteSerializer

    def get_queryset(self):
        return Product.objects.filter(
            menu__store=self.request.user.store
        ).prefetch_related('options__option_group')

    def get_serializer_context(self):
        return {'request': self.request}


# ═══════════════════════════════════════════════════════════════
# PUBLIC (عرض عام للزبون)
# ═══════════════════════════════════════════════════════════════

class StoreMenusPublicView(generics.ListAPIView):
    serializer_class   = MenuReadSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Menu.objects.filter(
            store_id=self.kwargs['store_id'],
            store__status='approved'
        ).prefetch_related('products__options__option_group')