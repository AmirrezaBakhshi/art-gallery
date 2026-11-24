from rest_framework.throttling import AnonRateThrottle


class GalleryLoginThrottle(AnonRateThrottle):
    scope = "gallery_login"


class GallerySignupThrottle(AnonRateThrottle):
    scope = "gallery_signup"
