from gluon.globals import current
from gluon.storage import Storage

db.define_table('plugin_social_auth_user',
                Field('provider', 'string', notnull=True, writable=False),
                Field('oauth_uid', 'string', notnull=True, writable=False, length=255),
                Field('extra_data', 'json', writable=False),
                Field('oauth_user', 'reference auth_user', writable=False, notnull=True))

db.define_table('plugin_social_auth_nonce',
                Field('server_url', 'string', notnull=True, readable=False, writable=False, length=255),
                Field('nonce_timestamp', 'integer', notnull=True, readable=False, writable=False),
                Field('salt', 'string', notnull=True, readable=False, writable=False, length=40))

db.define_table('plugin_social_auth_association',
                Field('server_url', 'string', notnull=True, readable=False, writable=False, length=255),
                Field('handle', 'string', notnull=True, readable=False, writable=False, length=255),
                Field('secret', 'string', notnull=True, readable=False, writable=False, length=255),
                Field('issued', 'integer', notnull=True, readable=False, writable=False),
                Field('lifetime', 'integer', notnull=True, readable=False, writable=False),
                Field('assoc_type', 'string', notnull=True, readable=False, writable=False, length=64))

_defaults = {'SOCIAL_AUTH_USER_MODEL': 'User',
             'SOCIAL_AUTH_USER_FIELDS': ['first_name', 'last_name', 'username', 'email'],
             'SOCIAL_AUTH_EXCEPTION_HANDLER': 'plugin_social_auth.utils.W2pExceptionHandler',
             'SOCIAL_AUTH_APP_INDEX_URL': None,

             'SOCIAL_AUTH_PIPELINE': (
                'plugin_social_auth.pipeline.clean_confirm_session',
                'social_core.pipeline.social_auth.social_details',
                'social_core.pipeline.social_auth.social_uid',
                'social_core.pipeline.social_auth.auth_allowed',
                'social_core.pipeline.social_auth.social_user',
                'plugin_social_auth.pipeline.confirm_new_user',
                'social_core.pipeline.user.get_username',
                'social_core.pipeline.user.create_user',
                'plugin_social_auth.pipeline.associate_user',
                'social_core.pipeline.social_auth.load_extra_data',
                'social_core.pipeline.user.user_details'),

             'SOCIAL_AUTH_DISCONNECT_PIPELINE': (
                'social_core.pipeline.disconnect.allowed_to_disconnect',
                'social_core.pipeline.disconnect.get_entries',
                'social_core.pipeline.disconnect.revoke_tokens',
                'plugin_social_auth.pipeline.disconnect'),

             'SOCIAL_AUTH_ENABLE_PERSONA': False,
             'SOCIAL_AUTH_CONFIRM_NEW_USER': False,
             'SOCIAL_AUTH_PROVIDERS': {},

             'SOCIAL_AUTH_UI_BOOTSTRAP': True,
             'SOCIAL_AUTH_UI_STYLE': 'buttons',
             'SOCIAL_AUTH_UI_ICONS': True,

             # Google OpenID should not be used with manual OpenID entry because
             # Google may use different ID's for different domains so it's not guaranteed to
             # always stay the same. If you want to use Google OpenId, use:
             # social.backends.google.GoogleOpenId (will use email as ID)
             # http://blog.stackoverflow.com/2010/04/openid-one-year-later/
             # http://blog.stackoverflow.com/2009/04/googles-openids-are-unique-per-domain/
             'SOCIAL_AUTH_DISALLOWED_OPENID_HOSTS': ['www.google.com', 'google.com']}

_plugins = PluginManager('social_auth', **_defaults)

if 'plugin_social_auth' not in session:
    session.plugin_social_auth = Storage()

# expose globals to plugin_social_auth
current.plugin_social_auth = Storage()
current.plugin_social_auth.session = session
current.plugin_social_auth.s = session.plugin_social_auth
current.plugin_social_auth.auth = auth
current.plugin_social_auth.db = db
current.plugin_social_auth.T = T
current.plugin_social_auth.plugin = _plugins.social_auth
current.plugin_social_auth.response = response
