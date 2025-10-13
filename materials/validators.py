from rest_framework import serializers
from urllib.parse import urlparse


def validate_youtube_only(value):
    """
    Валидатор для проверки, что ссылка ведет только на youtube.com
    """
    if value:
        parsed_url = urlparse(value)
        domain = parsed_url.netloc.lower()

        # Разрешаем только youtube.com и youtu.be (короткие ссылки YouTube)
        allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'www.youtu.be']

        if not any(domain.endswith(allowed_domain) for allowed_domain in allowed_domains):
            raise serializers.ValidationError(
                "Разрешены только ссылки на YouTube. Пожалуйста, используйте ссылки с youtube.com или youtu.be"
            )
    return value


class YouTubeValidator:
    """
    Класс-валидатор для проверки YouTube ссылок
    """

    def __init__(self, field):
        self.field = field

    def __call__(self, attrs):
        value = attrs.get(self.field)
        validate_youtube_only(value)