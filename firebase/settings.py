from django.conf import settings

FIREBASE_CONFIG = getattr(settings, "FIREBASE_CONFIG", {})

# Firebase
FIREBASE_CONFIG.setdefault("FIREBASE_SERVICE_ACCOUNT", None)
FIREBASE_CONFIG.setdefault("FIREBASE_WEBAPP_CONFIG", None)

# User model
FIREBASE_CONFIG.setdefault("USER_MODEL", settings.AUTH_USER_MODEL)
