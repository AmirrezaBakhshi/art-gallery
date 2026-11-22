from secrets import token_urlsafe

from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import GalleryTokenAuthentication
from .models import Gallary, Item, TargetFile
from .permissions import IsGalleryOwnerOrReadOnly
from .serializers import GallarySerializer, ItemSerializer, SignupSerializer, TargetFileSerializer
from .throttles import GalleryLoginThrottle


class GallerySignupView(ListCreateAPIView):
    queryset = Gallary.objects.all()
    serializer_class = SignupSerializer
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        # Public gallery directory never includes credentials or private tokens.
        return Response(GallarySerializer(self.get_queryset(), many=True, context={"request": request}).data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        gallery = serializer.save()
        return Response({
            "gallery": GallarySerializer(gallery, context={"request": request}).data,
            "token": gallery.api_token,
        }, status=status.HTTP_201_CREATED)


class GalleryView(RetrieveUpdateDestroyAPIView):
    queryset = Gallary.objects.all()
    serializer_class = GallarySerializer
    authentication_classes = (GalleryTokenAuthentication, SessionAuthentication)
    permission_classes = (IsGalleryOwnerOrReadOnly,)


class GalleryLoginView(APIView):
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

        # Upgrade legacy plaintext credentials on the first successful login.
        if not check_password(password, gallery.password):
            if gallery.password != password:
                return Response({"detail": "Invalid username or password."},
                                status=status.HTTP_400_BAD_REQUEST)
            gallery.password = make_password(password)
        if not gallery.api_token:
            gallery.api_token = token_urlsafe(32)
        gallery.save(update_fields=["password", "api_token"])
        return Response({
            "gallery": GallarySerializer(gallery, context={"request": request}).data,
            "token": gallery.api_token,
        })


class GalleryLogoutView(APIView):
    authentication_classes = (GalleryTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.api_token = token_urlsafe(32)
        request.user.save(update_fields=["api_token"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemListView(ListCreateAPIView):
    queryset = Item.objects.all().order_by("id")
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
    queryset = TargetFile.objects.all()
    serializer_class = TargetFileSerializer
    authentication_classes = (GalleryTokenAuthentication, SessionAuthentication)

    def get_permissions(self):
        return (AllowAny(),) if self.request.method in ("GET", "HEAD", "OPTIONS") else (IsAuthenticated(),)

    def perform_create(self, serializer):
        serializer.save(gallary=self.request.user)


class TargetFileView(RetrieveUpdateDestroyAPIView):
    queryset = TargetFile.objects.all()
    serializer_class = TargetFileSerializer
    authentication_classes = (GalleryTokenAuthentication, SessionAuthentication)
    permission_classes = (IsGalleryOwnerOrReadOnly,)
