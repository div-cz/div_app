from rest_framework.renderers import JSONRenderer

class HTTPSJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = renderer_context.get('request')
        if request is not None and 'https' in request._request.META['wsgi.url_scheme']:
            data = self._replace_http_with_https(data)
        return super().render(data, accepted_media_type, renderer_context)

    def _replace_http_with_https(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = self._replace_http_with_https(value)
        elif isinstance(data, list):
            data = [self._replace_http_with_https(item) for item in data]
        elif isinstance(data, str) and data.startswith('http://'):
            data = data.replace('http://', 'https://')
        return data