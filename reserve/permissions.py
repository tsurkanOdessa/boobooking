from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Owner'

class IsOwnerOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['Owner', 'Manager']

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.role == 'Manager'

class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['Admin', 'Manager']

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.role == 'Manager'