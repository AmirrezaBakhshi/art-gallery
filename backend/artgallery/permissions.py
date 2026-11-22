from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsGalleryOwnerOrReadOnly(BasePermission):
    """Allow public reads; only the owning authenticated gallery may mutate."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        gallery_id = getattr(obj, "gallary_id", getattr(obj, "id", None))
        return bool(request.user and request.user.is_authenticated and request.user.id == gallery_id)
