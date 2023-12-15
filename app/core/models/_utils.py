def get_default_media_format_audio() -> int:
    from .models import MediaFormat
    return MediaFormat.get_default_audio()
