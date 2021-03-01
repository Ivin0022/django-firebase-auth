import json
from firebase_admin import credentials, initialize_app
from .settings import FIREBASE_CONFIG

FIREBASE_SERVICE_ACCOUNT = FIREBASE_CONFIG['FIREBASE_SERVICE_ACCOUNT']

# TODO seprate out the error handling to diffrent file
if not FIREBASE_SERVICE_ACCOUNT:
    raise ImproperlyConfigured('you must set FIREBASE_SERVICE_ACCOUNT')

try:
    cert = json.loads(FIREBASE_SERVICE_ACCOUNT)
except ValueError:
    raise ImproperlyConfigured('FIREBASE_SERVICE_ACCOUNT must be in a json format')

firebase_cert = credentials.Certificate(cert=cert)

firebase_app = initialize_app(firebase_cert)
