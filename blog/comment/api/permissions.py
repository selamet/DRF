from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    # sayfa yüklenir yüklenmez tetiklenir
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    message = "You must be the owner of this object."

    # delete butonun tıklayınca tetiklenir
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
