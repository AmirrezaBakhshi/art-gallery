from datetime import timedelta
from secrets import token_urlsafe

from django.utils import timezone

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import GalleryTokenAuthentication, token_digest
from .models import Gallary, Item, TargetFile
from .permissions import IsGalleryOwnerOrReadOnly
from .serializers import GallarySerializer, ItemSerializer, SignupSerializer, TargetFileSerializer
from .throttles import GalleryLoginThrottle, GallerySignupThrottle


@method_decorator(csrf_protect, name="dispatch")
class GallerySignupView(ListCreateAPIView):
    queryset = Gallary.objects.all()
    serializer_class = SignupSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)
    def get_throttles(self):
        if self.request.method == "POST":
            return [GallerySignupThrottle()]
        return []

    def get(self, request, *args, **kwargs):
        # Public gallery directory never includes credentials or private tokens.
        return Response(GallarySerializer(self.get_queryset(), many=True, context={"request": request}).data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        gallery = serializer.save()
        response = Response({"gallery": GallarySerializer(gallery, context={"request": request, "include_private": True}).data}, status=status.HTTP_201_CREATED)
        get_token(request)
        response.set_cookie("gallery_session", gallery._issued_token, max_age=settings.GALLERY_SESSION_TTL_DAYS * 86400, httponly=True, secure=not settings.DEBUG, samesite=settings.SESSION_COOKIE_SAMESITE, path="/")
        return response


class GalleryView(RetrieveUpdateDestroyAPIView):
    queryset = Gallary.objects.all()
    serializer_class = GallarySerializer
    authentication_classes = (GalleryTokenAuthentication, SessionAuthentication)
    permission_classes = (IsGalleryOwnerOrReadOnly,)


@method_decorator(csrf_protect, name="dispatch")
class GalleryLoginView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (GalleryLoginThrottle,)

    def post(self, request):
        username = str(request.data.get("username") or "").strip()
        password = request.data.get("password") or ""
        if not username or not password:
            return Response({"detail": "Username and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            gallery = Gallary.objects.get(username=username)
        except Gallary.DoesNotExist:
            return Response({"detail": "Invalid username or password."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not check_password(password, gallery.password):
            return Response({"detail": "Invalid username or password."},
                            status=status.HTTP_400_BAD_REQUEST)
        raw_token = token_urlsafe(32)
        gallery.api_token = token_digest(raw_token)
        gallery.api_token_expires_at = timezone.now() + timedelta(days=settings.GALLERY_SESSION_TTL_DAYS)
        gallery.save(update_fields=["api_token", "api_token_expires_at"])
        response = Response({"gallery": GallarySerializer(gallery, context={"request": request, "include_private": True}).data})
        get_token(request)
        response.set_cookie("gallery_session", raw_token, max_age=settings.GALLERY_SESSION_TTL_DAYS * 86400, httponly=True, secure=not settings.DEBUG, samesite=settings.SESSION_COOKIE_SAMESITE, path="/")
        return response


class GalleryCSRFView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class GalleryLogoutView(APIView):
    authentication_classes = (GalleryTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.api_token = None
        request.user.api_token_expires_at = None
        request.user.save(update_fields=["api_token", "api_token_expires_at"])
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("gallery_session", path="/", samesite=settings.SESSION_COOKIE_SAMESITE)
        return response


class ItemListView(ListCreateAPIView):
    queryset = Item.objects.select_related("gallary").all().order_by("id")
    serializer_class = ItemSerializer
    authentication_classes = (GalleryTokenAuthentication, SessionAuthentication)

    def get_permissions(self):
        return (AllowAny(),) if self.request.method in ("GET", "HEAD", "OPTIONS") else (IsAuthenticated(),)

    def perform_create(self, serializer):
        serializer.save(gallary=self.request.user)


class ItemView(RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = (GalleryTokenAuthentication, SessionAuthentication)
    permission_classes = (IsGalleryOwnerOrReadOnly,)


class TargetFileListView(ListCreateAPIView):
    serializer_class = TargetFileSerializer
    authentication_classes = (GalleryTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Never expose target-file records or storage URLs across gallery accounts.
        return TargetFile.objects.select_related("gallary").filter(
            gallary=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(gallary=self.request.user)


class TargetFileView(RetrieveUpdateDestroyAPIView):
    serializer_class = TargetFileSerializer
    authentication_classes = (GalleryTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsGalleryOwnerOrReadOnly)

    def get_queryset(self):
        # Scope before object permission checks to prevent cross-gallery ID probing.
        return TargetFile.objects.filter(gallary=self.request.user)
