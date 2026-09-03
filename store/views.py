from rest_framework import viewsets, permissions, serializers
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Category, Store
from .serializers import (
    CategorySerializer, StoreSerializer, StoreApplicationSerializer
)


# سيريالايزر مبسط للعرض العام (بدون بيانات المالكين)
class PublicStoreSerializer(serializers.ModelSerializer):
    trade_name = serializers.CharField(
        source='store_information.trade_name'
    )
    wilaya = serializers.CharField(
        source='store_information.get_wilaya_display'
    )
    category = serializers.CharField(
        source='store_information.category.name'
    )

    class Meta:
        model = Store
        fields = ['id', 'trade_name', 'wilaya', 'category']


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/categories/
    GET /api/categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class StoreViewSet(viewsets.ModelViewSet):
    """
    POST   /api/stores/          → طلب انضمام (عام)
    GET    /api/stores/          → التاجر يشوف متجره
    GET    /api/stores/{id}/     → تفاصيل متجره
    GET    /api/stores/search/   → بحث عام بالاسم
    GET    /api/stores/browse/   → تصفح عام بالفئة
    PUT/PATCH/DELETE             → مغلقة كليا
    """
    http_method_names = ['get', 'post', 'head', 'options']
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.action in ['create', 'search', 'browse']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            if self.request.user.is_authenticated:
                return Store.objects.filter(
                    user=self.request.user
                ).select_related(
                    'store_information', 'store_contact_information'
                )
            return Store.objects.none()

        # search و browse
        return Store.objects.filter(
            status='approved'
        ).select_related('store_information__category')

    def create(self, request, *args, **kwargs):
        serializer = StoreApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        store = serializer.save()
        return Response(
            {
                "message": "تم استلام طلبك، سيتم مراجعته من الإدارة.",
                "store_id": store.id
            },
            status=201
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def search(self, request):
        """GET /api/stores/search/?q=اسم المتجر"""
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response({"detail": "يرجى إدخال كلمة البحث."}, status=400)

        stores = self.get_queryset().filter(
            store_information__trade_name__icontains=q
        )
        serializer = PublicStoreSerializer(stores, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def browse(self, request):
        """GET /api/stores/browse/?category=1"""
        stores = self.get_queryset()
        category_id = request.query_params.get('category')
        if category_id:
            stores = stores.filter(
                store_information__category_id=category_id
            )
        serializer = PublicStoreSerializer(stores, many=True)
        return Response(serializer.data)