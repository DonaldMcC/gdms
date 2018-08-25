# - Coding UTF8 -
#
# Networked Decision Making
# Development Sites (source code): http://github.com/DonaldMcC/gdms
#
# Demo Sites (Pythonanywhere)
#   http://netdecisionmaking.com/nds/
#   http://netdecisionmaking.com/gdmsdemo/
#
# License Code: MIT
# License Content: Creative Commons Attribution 3.0
#
# Also visit: www.web2py.com
# or Groups: http://groups.google.com/group/web2py
# For details on the web framework used for this development
#
# With thanks to Guido, Massimo and many other that make this sort of thing
# much easier than it used to be
# v4.3.0
#
# key changes - introduce fact or opinion classification of questions and probably add to userquestion to choose
# think facts should quote a source and maybe accept or reject - don't think they need multi-choice - but should
# be on the form
# thinking of having a general scoring what changes and what doesn't function
# master and subquestions have been added - would need to push into that and display levels on
# events and so forth - think we add questions and push them down mostly - but can drag to top and pull up again


import os
from gluon.tools import Auth, PluginManager, prettydate, Mail
from plugin_location_picker import IS_GEOLOCATION, location_widget
from gluon import *
from gluon.custom_import import track_changes

from gluon import current
from ndsfunctions import generate_thumbnail

# global setting for extra javasacript for data table export and d3 graph
load_dt_exp = False
load_graph = False

filename = 'private/appconfig.ini'
path = os.path.join(request.folder, filename)
if os.path.exists(path):
    useappconfig = True
else:
    useappconfig = False

usecategory = True

if useappconfig:
    from gluon.contrib.appconfig import AppConfig
    # once in production, remove reload=True to gain full speed
    myconf = AppConfig(reload=False)
    debug = myconf.take('developer.debug', cast=int)
    backend = myconf.take('search.backend')
    if myconf.take('site.require_https', cast=int):
        request.requires_https()
else:
    debug = False
    backend = 'SimpleBackend'

# once in production change to False
track_changes(debug)

if not request.env.web2py_runtime_gae:
    if useappconfig:
        db = DAL(myconf.take('db.uri'),
                 pool_size=myconf.take('db.pool_size', cast=int),
                 migrate=myconf.take('db.migrate', cast=int),
                 lazy_tables=myconf.take('db.lazy_tables', cast=int),
                 check_reserved=['all'])
    else:
        db = DAL('sqlite://storage.sqlite')
else:
    db = DAL('google:datastore+ndb')
    # store sessions and tickets there
    session.connect(request, response, db=db)

current.db = db

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

if useappconfig:
    response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked'
    response.form_label_separator = myconf.take('forms.separator')
    login = myconf.take('login.logon_methods')
    requires_login = myconf.take('site.require_login', cast=int)
    dbtype = myconf.take('db.dbtype')
    hostadds = myconf.take('google.hostadds', cast=int)
    ad_client = myconf.take('google.ad_client')
    ad_slot = myconf.take('google.ad_slot', cast=int)
    wa_id=myconf.take('knowledge.wolfram_alpha')
else:  # default values if not using appconfig
    response.formstyle = 'bootstrap3_inline'
    response.form_label_separator = ":"
    login = 'web2py'
    requires_login = False
    dbtype = 'sql'
    hostadds = False
    ad_client = None
    ad_slot = None
    wa_id=None


if login == 'socialauth':
    from plugin_social_auth.utils import SocialAuth
    auth = SocialAuth(db)
    username_field = True  # This is required
else:
    auth = Auth(db, hmac_key=Auth.get_or_create_key())
    username_field = False  # can set to true if you want login by username rather than email
plugins = PluginManager()

# all other tables in db_gdms.py but this needs to be defined before
# extra fields in auth not anymore as now derelationised for gae to reduce
# readcounts - so category continent country and subdivision and scope
# moved

userfields = [
    Field('numquestions', 'integer', default=0, readable=False, writable=False, label='Answered'),
    Field('score', 'integer', default=0, readable=False, writable=False, label='Score'),
    Field('rating', 'integer', default=0, readable=False, writable=False, label='Rating'),
    Field('userlevel', 'integer', default=1, readable=False, writable=False, label='Level'),
    Field('numcorrect', 'integer', default=0, readable=False, writable=False, label='Correct'),
    Field('numwrong', 'integer', default=0, readable=False, writable=False, label='Wrong'),
    Field('numpassed', 'integer', default=0, readable=False, writable=False, label='Passed'),
    Field('exclude_categories', 'list:string', label='Excluded Categories',
          comment="Select subjects you DON'T want questions on"),
    Field('continent', 'string', default='Unspecified', label='Continent'),
    Field('country', 'string', default='Unspecified', label='Country'),
    Field('subdivision', 'string', default='Unspecified', label='Sub-division'),

    Field('privacypref', 'string', default='Extreme', label='Privacy Preference',
          comment='Std user+avator, extreme is id only'),
    Field('avatar', 'upload'),
    Field('avatar_thumb', 'upload', compute=lambda r: generate_thumbnail(r['avatar'], 120, 120, True)),
    Field('show_help', 'boolean', default=True, label='Show help')]

use_geolocation = False
if useappconfig and myconf.take('google_maps.use', cast=int):
    use_geolocation = True
    GMAPKEY = myconf.get('google_maps.key')

use_address = False
if useappconfig and myconf.take('user.address', cast=int):
    use_address = True
    userfields.append(Field('address1', 'string', label='Address Line1'))
    userfields.append(Field('address2', 'string', label='Address Line2'))
    userfields.append(Field('address3', 'string', label='Address Line3'))
    userfields.append(Field('address4', 'string', label='Address Line4'))
    userfields.append(Field('zip', 'string', label='Zip/Postal Code'))
    userfields.append(Field('coord', 'string', label='Lat/Longitude'))
    userfields.append(Field('localrange', 'integer', default= 100, label='Radius for local issues', comment='In Kilometers',requires=IS_INT_IN_RANGE(1, 1000,
                      error_message='Must be between 1 and 1000')))

if not useappconfig or myconf.take('user.membernumber', cast=int):
    userfields.append(Field('membernumber', 'string', label='Membership #'))

userfields.append(Field('emaildaily', 'boolean', label='Send daily email'))
userfields.append(Field('emailweekly', 'boolean', default=True, label='Send weekly email'))
userfields.append(Field('emailmonthly', 'boolean', label='Send monthly email'))
userfields.append(Field('emailresolved', 'boolean', default=True, label='Email when my items resolved'))
userfields.append(Field('data_consent', 'boolean', default=False, label='I consent to Net Decision Making holding minimal personal'
                                                          ' information to support operation of this site - it is not shared with 3rd parties'
                        , requires=IS_NOT_EMPTY(error_message='You must consent to register')))

auth.settings.extra_fields['auth_user'] = userfields
auth.settings.username_case_sensitive = False
auth.settings.email_case_sensitive = False

# create all tables needed by auth if not custom tables
auth.define_tables(username=username_field)
auth.settings.auth_manager_role = 'manager'
auth.settings.logout_next = URL(args=request.args, vars=request.get_vars)


if useappconfig and myconf.take('user.disablereg', cast=int):
    # used to block registration if required
    auth.settings.actions_disabled.append('register')

# configure auth policy
if useappconfig:
    auth.settings.registration_requires_verification = myconf.take('user.verification', cast=int)
    auth.settings.registration_requires_approval = myconf.take('user.approval', cast=int)
else:
    auth.settings.registration_requires_verification = False
    auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

db.auth_user.privacypref.requires = IS_IN_SET(['Standard', 'Extreme'])

if not useappconfig or myconf.take('user.address', cast=int):
    db.auth_user.coord.requires = IS_GEOLOCATION()
    db.auth_user.coord.widget = location_widget()

# recommended and supported login methods are now web2py and socialauth - other code
# is left as legacy but not supported

if request.env.web2py_runtime_gae and login == 'google':
    from gluon.contrib.login_methods.gae_google_account import GaeGoogleAccount
    auth.settings.login_form = GaeGoogleAccount()
elif login == 'janrain':  # this is limited by Janrain providers
    # from gluon.contrib.login_methods.rpx_account import RPXAccount
    from gluon.contrib.login_methods.rpx_account import use_janrain
    use_janrain(auth, filename='private/janrain.key')
elif login == 'web2pyandjanrain':  # this is now proving useless as no providers really work
    # Dual login sort of working but not fully tested with Janrain - doesnt work with gae
    # from gluon.contrib.login_methods.extended_login_form import ExtendedLoginForm
    # from gluon.contrib.login_methods.rpx_account import RPXAccount
    # other_form = use_janrain(auth, filename='private/janrain.key')
    # auth.settings.login_form = ExtendedLoginForm(auth, other_form, signals=['token'])
    from gluon.contrib.login_methods.extended_login_form import ExtendedLoginForm
    from gluon.contrib.login_methods.rpx_account import RPXAccount
    filename = 'private/janrain.key'
    path = os.path.join(current.request.folder, filename)
    if os.path.exists(path):
        request = current.request
        domain, key = open(path, 'r').read().strip().split(':')
        host = current.request.env.http_host
        url = URL('default', 'user', args='login', scheme=True)
        other_form = RPXAccount(request, api_key=key, domain=domain, url=url)
        auth.settings.login_form = ExtendedLoginForm(auth, other_form, signals=['token'])
elif login == 'socialauth':
    auth.settings.actions_disabled = ['register', 'change_password', 'request_reset_password']

    # Make user props readonly since these will automatically be updated
    # when the user logs on with a new social account anyway.
    # NOTE: this fails when lazy tables used.
    for prop in ['first_name', 'last_name', 'email']:
        auth.settings.table_user[prop].writable = False

        ############################################################################
        ##
        ## w2p-social-auth plugin configuration
        ##
        ############################################################################

        # Configure your API keys
        # This needs to be replaced by your actual API keys

        # Configure your API keys
        # This needs to be replaced by your actual API keys
        plugins.social_auth.SOCIAL_AUTH_TWITTER_KEY = myconf.take('psa.twitter_consumer_key')
        plugins.social_auth.SOCIAL_AUTH_TWITTER_SECRET = myconf.take('psa.twitter_secret_key')
        plugins.social_auth.SOCIAL_AUTH_FACEBOOK_KEY = myconf.take('psa.facebook_app_id')
        plugins.social_auth.SOCIAL_AUTH_FACEBOOK_SECRET = myconf.take('psa.facebook_app_secret')
        plugins.social_auth.SOCIAL_AUTH_GOOGLE_PLUS_KEY = myconf.take('psa.google_client_id')
        plugins.social_auth.SOCIAL_AUTH_GOOGLE_PLUS_SECRET = myconf.take('psa.google_client_secret')
        plugins.social_auth.SOCIAL_AUTH_LIVE_KEY = myconf.take('psa.live_key')
        plugins.social_auth.SOCIAL_AUTH_LIVE_SECRET = myconf.take('psa.live_secret')
        # plugins.social_auth.SOCIAL_AUTH_LIVE_LOGIN_REDIRECT_URL = 'http://www.netdecisionmaking.com/gdms/logged-in/'

        # Configure PSA with all required backends
        # Replace this by the backends that you want to use and have API keys for
        plugins.social_auth.SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
            # You need this one to enable manual input for openid.
            # It must _not_ be configured in SOCIAL_AUTH_PROVIDERS (below)
            'social_core.backends.google.GooglePlusAuth',
            'social_core.backends.live.LiveOAuth2',
            'social_core.backends.twitter.TwitterOAuth',
            'social_core.backends.facebook.FacebookOAuth2')

        # Configure the providers that you want to show in the login form.
        # <backend name> : <display name>
        # (You can find the backend name in the backend files as configured above.)
        # Replace this by the backends you want to enable
        # plugins.social_auth.SOCIAL_AUTH_PROVIDERS = {
        #    'live': 'Live',
        #    'twitter': 'Twitter',
        #    'facebook': 'Facebook',
        #    'google-plus': 'Google+',
        #    'persona': 'Mozilla Persona'}

        plugins.social_auth.SOCIAL_AUTH_PROVIDERS = {
            'twitter': 'Twitter',
            'facebook': 'Facebook',
            'google-plus': 'Google+',
            'live': 'Live'}

    # Configure app index URL. This is where you are redirected after logon when
    # auth.settings.logout_next is not configured.
    # If both are not configured there may be no redirection after logout! (returns 'None')
    plugins.social_auth.SOCIAL_AUTH_APP_INDEX_URL = URL('init', 'default', 'index')

    # Remove or set to False if you are not using Persona
    plugins.social_auth.SOCIAL_AUTH_ENABLE_PERSONA = True

    # w2p-social-auth can be configured to show a dropdown or buttons.
    # 'dropdown' does not require javascript (except for Persona backend) and
    # 'buttons' requires js and jquery to be loaded.
    # Uncomment this line to use dropdown in stead of the default buttons
    # plugins.social_auth.SOCIAL_AUTH_UI_STYLE = 'dropdown'

    # This setting only has effect when SOCIAL_AUTH_UI_STYLE = 'buttons'
    # Uuncomment this line to apply bootstrap styles to the buttons
    # plugins.social_auth.SOCIAL_AUTH_UI_BOOTSTRAP = False

    # Uncomment this line to remove icons from buttons
    # plugins.social_auth.SOCIAL_AUTH_UI_ICONS = False