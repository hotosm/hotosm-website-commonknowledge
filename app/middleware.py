# myapp/middleware.py
from django.conf import settings
from django.http import HttpResponsePermanentRedirect

from app.utils.url import urljoin


class StagingDomainRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().partition(":")[0]
        if host in settings.REDIRECT_FROM_HOSTS:
            new_url = urljoin(settings.BASE_URL, request.path.lstrip("/"))
            return HttpResponsePermanentRedirect(new_url)
        else:
            return self.get_response(request)
