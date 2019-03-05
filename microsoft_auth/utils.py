from .conf import config as global_config


def get_scheme(request, config=None):
    if config is None:
        config = global_config

    scheme = "https"
    if config.DEBUG and request is not None:
        if "HTTP_X_FORWARDED_PROTO" in request.META:
            scheme = request.META["HTTP_X_FORWARDED_PROTO"]
        else:
            scheme = request.scheme
    return scheme
