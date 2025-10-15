from rest_framework import serializers
from urllib.parse import urlparse


def validate_youtube_only(value):
    """
    Валидатор для проверки, что ссылка ведет только на youtube.com
    """
    if value:
        parsed_url = urlparse(value)
        domain = parsed_url.netloc.lower()

        allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'www.youtu.be']

        if not any(allowed_domain in domain for allowed_domain in allowed_domains):
            raise serializers.ValidationError(
                "Разрешены только ссылки на YouTube. Пожалуйста, используйте ссылки с youtube.com или youtu.be"
            )
    return value