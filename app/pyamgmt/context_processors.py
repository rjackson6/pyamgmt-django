from django.conf import settings


def static_urls(_request) -> dict:
    stage = 'debug' if settings.DEBUG is True else 'prod'
    return {
        'JQUERY_JS_URL': settings.STATIC_RESOURCES['JQUERY_JS'][stage],
        'PLOTLY_JS_URL': settings.STATIC_RESOURCES['PLOTLY_JS'][stage],
        'SELECT2_CSS_URL': settings.STATIC_RESOURCES['SELECT2_CSS'][stage],
        'SELECT2_JS_URL': settings.STATIC_RESOURCES['SELECT2_JS'][stage]
    }
