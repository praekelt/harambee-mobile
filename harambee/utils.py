from django.shortcuts import HttpResponse


def resolve_http_method(request, methods):
    if isinstance(methods, list):
        methods = dict([(func.__name__.lower(), func) for func in methods])
    if request.method.lower() not in methods.keys():
        return HttpResponse(status=501)
    return methods[request.method.lower()]()