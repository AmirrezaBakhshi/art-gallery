from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from artgallery.views import (
    GalleryLoginView, GalleryLogoutView, GallerySignupView, GalleryView, GalleryCSRFView,
    ItemListView, ItemView, TargetFileListView, TargetFileView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/csrf/", GalleryCSRFView.as_view(), name="gallery-csrf"),
    path("api/auth/login/", GalleryLoginView.as_view(), name="gallery-login"),
    path("api/auth/logout/", GalleryLogoutView.as_view(), name="gallery-logout"),
    path("api/gallaries/", GallerySignupView.as_view(), name="gallery-list-create"),
    re_path(r"^api/gallaries/(?P<pk>\d+)/$", GalleryView.as_view(), name="gallery-detail"),
    path("api/targetfiles/", TargetFileListView.as_view(), name="targetfile-list-create"),
    re_path(r"^api/targetfiles/(?P<pk>\d+)/$", TargetFileView.as_view(), name="targetfile-detail"),
    path("api/items/", ItemListView.as_view(), name="item-list-create"),
    re_path(r"^api/items/(?P<pk>\d+)/$", ItemView.as_view(), name="item-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
