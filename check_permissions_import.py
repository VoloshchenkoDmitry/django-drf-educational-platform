import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    from materials.permissions import IsOwnerOrModerator, CanCreateLesson, CanCreateCourse
    print("✓ All permissions imported successfully!")
    print(f"  - IsOwnerOrModerator: {IsOwnerOrModerator}")
    print(f"  - CanCreateLesson: {CanCreateLesson}")
    print(f"  - CanCreateCourse: {CanCreateCourse}")
except ImportError as e:
    print(f"✗ Import failed: {e}")