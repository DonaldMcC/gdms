from social_core.strategy import BaseTemplateStrategy, BaseStrategy
from gluon.globals import current
from gluon.http import redirect


# FIXME Not sure yet how this is used and how to implement it
class W2PTemplateStrategy(BaseTemplateStrategy):
    def render_template(self, tpl, context):
        return tpl

    def render_string(self, html, context):
        return html


class W2PStrategy(BaseStrategy):
    DEFAULT_TEMPLATE_STRATEGY = W2PTemplateStrategy

    def __init__(self, storage, request=current.request, tpl=None):
        self.request = request
        self.session = current.plugin_social_auth.s
        self.plugin = current.plugin_social_auth.plugin
        super(W2PStrategy, self).__init__(storage, tpl)

    def request_data(self, merge=True):
        """Return current request data (POST or GET)"""
        if not self.request:
            return {}
        if merge:
            data = self.request.vars
        elif self.request.env.request_method == 'POST':
            data = self.request.post_vars
        else:
            data = self.request.get_vars
        return data

    def request_host(self):
        """Return current host value"""
        if self.request:
            return self.request.env.http_host

    def session_get(self, name, default=None):
        """Return session value for given key"""
        return self.session.get(name, default)

    def session_set(self, name, value):
        """Set session value for given key"""
        self.session[name] = value

    def session_pop(self, name):
        """Pop session value for given key"""
        self.session.pop(name, None)

    def get_setting(self, name):
        """Return value for given setting name"""
        value = getattr(self.plugin, name)
        if value is not None:
            return value
        raise AttributeError()

    def redirect(self, url):
        """Return a response redirect to the given URL"""
        return redirect(url)

    def html(self, content):
        """Return HTTP response with given content"""
        return content

    def render_html(self, tpl=None, html=None, context=None):
        """Render given template or raw html with given context"""
        # FIXME Don't know yet what to do with this
        return html

    def build_absolute_uri(self, path=None):
        """Build absolute URI with given (optional) path"""
        # FIXME seems little awkward
        if path.startswith('http://') or path.startswith('https://'):
            return path
        host = self.request.env.http_host
        if host.endswith('/') and path.startswith('/'):
            path = path[1:]

        return self.request.env.wsgi_url_scheme + '://' + host + (path or '')

    # def authenticate(self, backend, *args, **kwargs):
    #    kwargs['strategy'] = self
    #    kwargs['storage'] = self.storage
    #    kwargs['backend'] = backend
    #    return
