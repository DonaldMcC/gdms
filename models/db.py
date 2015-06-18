# - Coding UTF8 -
#
# Networked Decision Making
# Site:
#
#
# Also visit: www.web2py.com
#             or Groups: http://groups.google.com/group/web2py
# 	For details on the web framework used for this development
# test amend for git pull on pythonanywhere


#for testing remove later
import os
#import urllib
from gluon import *
#from gluon.tools import fetch
#from gluon.storage import Storage
#import gluon.contrib.simplejson as json
from gluon.custom_import import track_changes;
from gluon import current


track_changes(True)
#

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    if settings.database=='sqlite':
        db = DAL('sqlite://storage.sqlite')
    else:
        filename = 'private/mysql.key'
        path = os.path.join(request.folder, filename)
        if os.path.exists(path):
            mylogin =  open(path, 'r').read().strip()
            # mysql://username:password@localhost/test
            db = DAL(mylogin)
        else:
            print 'no login key'
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    #db = DAL('google:datastore+ndb', lazy_tables=True) # lets try new one below
    #db = DAL('google:datastore+ndb') # lets try new one below
    #db = DAL('google:datastore', lazy_tables=True) # lets try new one below
    #db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    #session.connect(request, response, db=db)
    # session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    #from gluon.contrib.memdb import MEMDB
    #from google.appengine.api.memcache import Client
    #session.connect(request, response, db = MEMDB(Client()))

    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)


current.db = db

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
#response.generic_patterns = ['*'] if request.is_local else []
response.generic_patterns = ['*']
response.formstyle = 'bootstrap3_inline'  # or 'bootstrap3_stacked'
#response.formstyle = 'bootstrap3_stacked'
#response.formstyle = 'bootstrap3_stacked'
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

import os
from gluon.tools import Auth, Crud, Service, PluginManager, prettydate, Mail


auth = Auth(db, hmac_key=Auth.get_or_create_key())


crud, service, plugins = Crud(db), Service(), PluginManager()

#all other tables in db_gdms.py but this needs to be defined before
#extra fields in auth not anymore as now derelationised for gae to reduce
#readcounts - so category continent country and subdivision and scope 
#moved

#think num questions will become list int for numanswers and comments as well but not now

userfields = [
    Field('numquestions', 'integer', default=0, readable=False, writable=False, label='Answered'),
    Field('score', 'integer', default=0, readable=False, writable=False, label='Score'),
    Field('rating', 'integer', default=0, readable=False, writable=False, label='Rating'),
    Field('level', 'integer', default=1, readable=False, writable=False, label='Level'),
    Field('numcorrect', 'integer', default=0, readable=False, writable=False, label='Correct'),
    Field('numwrong', 'integer', default=0, readable=False, writable=False, label='Wrong'),
    Field('numpassed', 'integer', default=0, readable=False, writable=False, label='Passed'),
    Field('exclude_categories', 'list:string', label='Excluded Categories',
          comment="Select subjects you DON'T want questions on"),
    Field('continent', 'string', default='Unspecified', label='Continent'),
    Field('country', 'string', default='Unspecified', label='Country'),
    Field('subdivision', 'string', default='Unspecified', label='Sub-division'),
    Field('privacypref', 'string', default='Standard', label='Privacy Preference',
          comment='Std user+avator, extreme is id only'),
    Field('avatar', 'upload'),
    Field('avatar_thumb', 'upload', compute=lambda r: generate_thumbnail(r['avatar'], 120, 120, True)),
    Field('show_help','boolean',default=True,label='Show help')]

if settings.address:
    userfields.append(Field('address1', 'string', label='Address Line1'))
    userfields.append(Field('address2', 'string', label='Address Line2'))
    userfields.append(Field('address3', 'string', label='Address Line3'))
    userfields.append(Field('address4', 'string', label='Address Line4'))
    userfields.append(Field('zip', 'string', label='Zip/Postal Code'))

if settings.membernumber:
    userfields.append(Field('membernumber', 'string', label='Membership #'))

userfields.append(Field('emaildaily', 'boolean', label='Send daily email'))
userfields.append(Field('emailweekly', 'boolean', label='Send weekly email'))
userfields.append(Field('emailmonthly', 'boolean', label='Send monthly email'))
userfields.append(Field('emailresolved', 'boolean', default=True, label='Email when my items resolved'))
 
auth.settings.extra_fields['auth_user'] = userfields


## create all tables needed by auth if not custom tables
auth.define_tables(username=True)

#auth.settings.manager_group_role = 'manager'
#below was previous suggestion and seems to be required for 260 again
auth.settings.auth_manager_role = 'manager'

## configure auth policy
auth.settings.registration_requires_verification = settings.verification
auth.settings.registration_requires_approval = settings.approval
auth.settings.reset_password_requires_verification = True

db.auth_user.privacypref.requires = IS_IN_SET(['Standard', 'Extreme'])

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
## if you don't want to use then just dont setup a janrain.key file
## this works if key supplied - however not currently using as janrain doesn't 
## appear to work with ie10 - looks like python social auth will be the way to go
## here in due course
if request.env.web2py_runtime_gae and settings.logon_methods == 'google':
    from gluon.contrib.login_methods.gae_google_account import GaeGoogleAccount
    auth.settings.login_form = GaeGoogleAccount()
elif settings.logon_methods == 'janrain': # this is limited by Janrain providers
    #from gluon.contrib.login_methods.rpx_account import RPXAccount
    from gluon.contrib.login_methods.rpx_account import use_janrain
    use_janrain(auth, filename='private/janrain.key')
    #auth.settings.login_form = RPXAccount(request,
    #api_key='4f608d8fa6a0ad46654e51f484fc504334a5ba01',
    #domain='netdecisionmaking',
    #url = "https://testdecisionmaking.appspot.com/%s/default/user/login" % request.application)
elif settings.logon_methods == 'web2pyandjanrain': # this is now proving useless as no providers really work
    #Dual login sort of working but not fully tested with Janrain - doesnt work with gae
    #from gluon.contrib.login_methods.extended_login_form import ExtendedLoginForm
    #from gluon.contrib.login_methods.rpx_account import RPXAccount
    #other_form = use_janrain(auth, filename='private/janrain.key')
    #auth.settings.login_form = ExtendedLoginForm(auth, other_form, signals=['token'])
    from gluon.contrib.login_methods.extended_login_form import ExtendedLoginForm
    from gluon.contrib.login_methods.rpx_account import RPXAccount
    filename='private/janrain.key'
    path = os.path.join(current.request.folder, filename)
    if os.path.exists(path):
        request = current.request
        domain, key = open(path, 'r').read().strip().split(':')
        host = current.request.env.http_host
        url = URL('default', 'user', args='login', scheme=True)
        other_form = RPXAccount(request,
        api_key=key,
        domain=domain,
        url = url)
        auth.settings.login_form = ExtendedLoginForm(auth, other_form, signals=['token'])
elif settings.logon_methods == 'authomatic': # this is under construction
    from authomatic import Authomatic
    from authomat import Web2pyAdapter

    from authomatic.providers import oauth2, oauth1, openid, gaeopenid

    CONFIG = {
    'tw': { # Your internal provider name

        # Provider class
        'class_': oauth1.Twitter,

        # Twitter is an AuthorizationProvider so we need to set several other properties too:
        'consumer_key': '########################',
        'consumer_secret': '########################',
    },

    'fb': {

        'class_': oauth2.Facebook,

        # Facebook is an AuthorizationProvider too.
        'consumer_key': '########################',
        'consumer_secret': '########################',

        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['user_about_me', 'email', 'publish_stream', 'read_stream'],
    },

    'gae_oi': {

        # OpenID provider based on Google App Engine Users API.
        # Works only on GAE and returns only the id and email of a user.
        # Moreover, the id is not available in the development environment!
        'class_': gaeopenid.GAEOpenID,
    },

    'oi': {

        # OpenID provider based on the python-openid library.
        # Works everywhere, is flexible, but requires more resources.
        'class_': openid.OpenID,
    }}
    authomatic = Authomatic(CONFIG, 'secret')


#########################################################################
## Define your tables below (or better in another model file)
##
## >>>setup tables are all defined in db__first.py
## >>>main tables are all defined in db_gdms.py
#########################################################################
