import os
from django.conf import settings

STRIPE_API_KEY = getattr(settings, 'STRIPE_API_KEY', os.getenv('STRIPE_API_KEY', 'sk_test_default_key'))
STRIPE_PUBLISHABLE_KEY = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_default_key'))