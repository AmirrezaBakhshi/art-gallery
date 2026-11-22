from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from .models import Gallary


class GalleryTokenAuthentication(BaseAuthentication):
    """Authenticate gallery accounts using Authorization: Bearer <token>."""

    keyword = b"bearer"

    def authenticate(self, request):
        parts = get_authorization_header(request).split()
        if not parts:
            return None
        if parts[0].lower() != self.keyword:
            return None
        if len(parts) != 2:
            raise AuthenticationFailed("Invalid Authorization header.")
        try:
            token = parts[1].decode("utf-8")
        except UnicodeError as exc:
            raise AuthenticationFailed("Invalid token.") from exc
        try:
            gallery = Gallary.objects.get(api_token=token)
        except Gallary.DoesNotExist as exc:
            raise AuthenticationFailed("Invalid or expired token.") from exc
        return gallery, token
