import hashlib

from rest_framework.authentication import BaseAuthentication, get_authorization_header, SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone

from .models import Gallary


def token_digest(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class GalleryTokenAuthentication(BaseAuthentication):
    """Authenticate bearer tokens or secure HttpOnly gallery session cookies."""

    keyword = b"bearer"

    def authenticate(self, request):
        parts = get_authorization_header(request).split()
        token = None
        from_cookie = False
        if parts:
            if parts[0].lower() != self.keyword or len(parts) != 2:
                raise AuthenticationFailed("Invalid Authorization header.")
            try:
                token = parts[1].decode("utf-8")
            except UnicodeError as exc:
                raise AuthenticationFailed("Invalid token.") from exc
        else:
            token = request.COOKIES.get("gallery_session")
            from_cookie = bool(token)

        if not token:
            return None
        try:
            gallery = Gallary.objects.get(api_token=token_digest(token))
        except Gallary.DoesNotExist as exc:
            if from_cookie:
                return None
            raise AuthenticationFailed("Invalid or expired token.") from exc

        if not gallery.api_token_expires_at or gallery.api_token_expires_at <= timezone.now():
            if from_cookie:
                return None
            raise AuthenticationFailed("Session expired. Please sign in again.")
        if from_cookie:
            SessionAuthentication().enforce_csrf(request)
        return gallery, token
