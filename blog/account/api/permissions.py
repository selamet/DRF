from rest_framework.permissions import BasePermission


class NotAuthenticated(BasePermission):
    # sayfa yüklenir yüklenmez tetiklenir
    message ="Çıkış yapmanız gerekir"
    def has_permission(self, request, view):
        return not request.user and not request.user.is_authenticated
