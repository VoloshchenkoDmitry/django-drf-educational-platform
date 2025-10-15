import os
import django
import sys
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import reverse
from rest_framework.test import APIClient
from materials.models import Course, Lesson
from users.models import User

print("=== MINIMAL DEBUG TEST ===")

# Создаем уникальные тестовые данные с timestamp
timestamp = datetime.now().strftime("%H%M%S")
test_email = f'test{timestamp}@test.com'

# Создаем тестовые данные
user = User.objects.create_user(email=test_email, password='testpass123')
course = Course.objects.create(title=f'Test Course {timestamp}', owner=user)
lesson = Lesson.objects.create(title=f'Test Lesson {timestamp}', course=course, owner=user)

client = APIClient()

print("1. Testing URL resolution...")
try:
    url = reverse('lesson-list')
    print(f"   ✓ URL resolved: {url}")
except Exception as e:
    print(f"   ✗ URL resolution failed: {e}")
    sys.exit(1)

print("2. Testing unauthenticated request...")
response = client.get(reverse('lesson-list'))
print(f"   Status: {response.status_code}")
if hasattr(response, 'data'):
    print(f"   Data: {response.data}")
else:
    print(f"   Content: {response.content}")

print("3. Testing authenticated request...")
client.force_authenticate(user=user)
response = client.get(reverse('lesson-list'))
print(f"   Status: {response.status_code}")
if hasattr(response, 'data'):
    print(f"   Data: {response.data}")
else:
    print(f"   Content: {response.content}")

# Cleanup
lesson.delete()
course.delete()
user.delete()

print("=== DEBUG TEST COMPLETE ===")