from rest_framework.throttling import AnonRateThrottle


class GalleryLoginThrottle(AnonRateThrottle):
    scope = "gallery_login"
