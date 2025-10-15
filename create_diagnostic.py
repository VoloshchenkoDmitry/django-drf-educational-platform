# Временный скрипт для диагностики
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import reverse, resolve

try:
    print("Testing URLs...")
    print("Lesson list:", reverse('lesson-list'))
    print("✓ Lesson list URL works")
except Exception as e:
    print(f"✗ Lesson list URL failed: {e}")

try:
    print("Subscription:", reverse('subscription'))
    print("✓ Subscription URL works")
except Exception as e:
    print(f"✗ Subscription URL failed: {e}")

try:
    print("Course list:", reverse('course-list'))
    print("✓ Course list URL works")
except Exception as e:
    print(f"✗ Course list URL failed: {e}")