
from authomatic.adapters import BaseAdapter


class Web2pyAdapter(BaseAdapter):
    """
    Adapter for the |web2py| framework.
    """

    def __init__(self, request, response):
        """
        :param request:
            An instance of the web2py request class

        :param response:
            An instance of the web2py response class
        """
        self.request = request
        self.response = response

    @property
    def params(self):
        return dict(self.request.REQUEST)

    @property
    def url(self):
        return self.request.build_absolute_uri(self.request.path)

    @property
    def cookies(self):
        return dict(self.request.COOKIES)

    def write(self, value):
        self.response.write(value)

    def set_header(self, key, value):
        self.response[key] = value

    def set_status(self, status):
        status_code, reason = status.split(' ', 1)
        self.response.status_code = int(status_code)