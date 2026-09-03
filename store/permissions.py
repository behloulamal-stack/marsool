from rest_framework import permissions


class IsApprovedStoreOwner(permissions.BasePermission):
    """يسمح فقط لتاجر عندو متجر approved"""
    def has_permission(self, request, view):
        store = getattr(request.user, 'store', None)
        return bool(store and store.status == 'approved')