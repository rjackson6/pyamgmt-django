from core.models.config import Config, Options


DEFAULTS = {
    Options.ROOT_HEADER_TEXT.value: 'Home'
}


def config_context(_request) -> dict:
    config = {d['option']: d['value'] for d in Config.objects.values()}
    for option in Options:
        if option not in config:
            config[option] = DEFAULTS[option]
    return {
        'CONFIG': config
    }
