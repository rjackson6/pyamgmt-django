import pprint


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Before the view
        print(request.user)

        response = self.get_response(request)
        # After the view
        print(request.user)
        return response


class DebugRequestMetaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        pprint.pp(request.META)
        response = self.get_response(request)
        return response
