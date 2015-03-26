# - Coding UTF8 -
#
# Networked Decision Making
# Site:
#
#
# Also visit: www.web2py.com
#             or Groups: http://groups.google.com/group/web2py
# 	For details on the web framework used for this development
#
#
# This file in particular borrows heavily from web2py appliance tiny website
#########################################################################

# Things to be initialized before main model

from os import path
import datetime


not_empty = IS_NOT_EMPTY()

db.define_table('init',
                Field('website_init', 'boolean', default=False))

db.define_table('website_parameters',
                Field('website_name_long', label=T('Website name long'), comment=T('Shown in the banner footer')),
                Field('website_name', label=T('Website name'), comment=T('Shown in top left logo')),
                Field('website_init', 'boolean', default=False, label=T('Website Setup'),
                      comment=T('Set to True once initialised')),
                Field('website_title', label=T('Website title'),
                      comment=T('Displayed instead of the banner if "with_banner"=False')),
                Field('website_subtitle', label=T('Website subtitle'), comment=T('Shown in the banner footer')),
                Field('website_url', label=T('Url'), comment=T('URL of the website')),
                Field('longdesc', 'text', label=T('Long Description'), comment=T('Subject of the website')),
                Field('shortdesc', label=T('Url'), comment=T('Short Description of the website')),
                Field('level1desc', label=T('Level1Desc'), comment=T('First Location Level')),
                Field('level2desc', label=T('Level2Desc'), comment=T('Second Location Level')),
                Field('level3desc', label=T('Level3Desc'), comment=T('Third Location Level')),
                Field('force_language', label=T('Force a language (en, it, es, fr, ...)')),
                Field('google_analytics_id', label=T('Google analytics id'),
                      comment=T('Your Google Analytics account ID')),
                Field('seo_website_title', label=T('SEO : Website title'),
                      comment=T('Displayed in <title> tag of the HTML source code')),
                Field('seo_meta_author', label=T('SEO : Meta "author"'),
                      comment=T('Displayed in <meta author> tag of the HTML source code')),
                Field('seo_meta_description', label=T('SEO : Meta "description"'),
                      comment=T('Displayed in <meta description> tag of the HTML source code')),
                Field('seo_meta_keywords', label=T('SEO : Meta "keywords"'),
                      comment=T('Displayed in <meta keywords> tag of the HTML source code')),
                Field('seo_meta_generator', label=T('SEO : Meta "generator"'),
                      comment=T('Displayed in <meta generator> tag of the HTML source code')),
                Field('quests_per_page', 'integer', default=20, label=T('Mail server port'),
                      comment=T('Port of the mailserver (used to send email in forms)')),
                Field('comments_per_page', 'integer', default=20, label=T('Mail server port'),
                      comment=T('Port of the mailserver (used to send email in forms)')))

db.website_parameters.website_url.requires = IS_EMPTY_OR(IS_URL())



db.define_table('category',
                Field('cat_desc', 'string', label='Category', requires=[not_empty, IS_SLUG(),
                                                                    IS_NOT_IN_DB(db, 'category.cat_desc'), IS_LOWER()]),
                Field('categorydesc', 'text', label='Description'),
                format='%(cat_desc)s')

# this will contain all groups setup to restrict acess to questions
db.define_table('access_group',
                Field('group_name', 'string', label='Group Name', requires=[not_empty, IS_SLUG(), IS_NOT_IN_DB(db, 'access_group.group_name'), IS_LOWER()]),
                Field('group_desc', 'text', label='Description'),
                Field('group_type', 'string', default='public', requires=(IS_IN_SET(['all', 'public', 'apply', 'invite', 'admin']))),
                Field('owner', 'reference auth_user', writable=False, readable=False, default=auth.user_id),
                Field('createdate', 'datetime', default=request.utcnow, writable=False, readable=False),
                format='%(group_name)s')

#db.access_group.group_name.requires = [not_empty, IS_NOT_IN_DB(db, 'access_group.group_name')]


db.define_table('group_members',
                Field('access_group', 'reference access_group'),
                Field('auth_userid', 'reference auth_user'),
                Field('user_role', default='member',requires=(IS_IN_SET(['member', 'admin']))),
                format='%access_group')

# this will contain the options for grouptypes in due course
db.define_table('accgrouptype',
                Field('grouptype', 'string', requires=IS_IN_SET(['public', 'apply', 'invite', 'admin']))
                )

db.accgrouptype.grouptype.requires = [not_empty, IS_NOT_IN_DB(db, 'accgrouptype.grouptype')]

db.access_group._after_insert.append(lambda fields, id: group_members_insert(fields, id))


def group_members_insert(fields, id):
    """
    :param fields: question fields
    :param id: question id
    :return: True
    This ensures that creator of a group is automatically a member of it at present all users are created as members and 
    admins should switch to admin if they dont want to get questions relating to the group
    """
    db.group_members.insert(access_group=id,auth_userid=auth.user_id)
    return


# so for now a public group can be joined by anyone and they can be viewed with a button to join
# groups that accept applications will also be viewable and applications will go to the owner for
# approval - invites can be sent to people to confirm they want to join and admin just bascically means
# admin appoints and probalby setup the admin piece of this first and then add the user functions later

labeltoplevel='TestCont'
labelmidlevel='TestCountry'
labellowlevel='TestSub'
tmplabel='Sub-Division eg State, Province, County'

db.define_table('continent',
                Field('continent_name', 'string', label=labeltoplevel, requires=[not_empty, IS_SLUG(),
                    IS_NOT_IN_DB(db, 'continent.continent_name')]),format='%(continent_name)s')

db.define_table('country',
                Field('country_name', 'string', label=labelmidlevel, requires=[not_empty, IS_SLUG(),
                                                                           IS_NOT_IN_DB(db, 'country.country_name')]),
                Field('continent', 'string', label='Continent'),
                format='%(country_name)s')

db.define_table('subdivision',
                Field('subdiv_name', 'string', label=labellowlevel),
                Field('country', 'string'),
                format='%(subdiv_name)s')

db.define_table('scope',
                Field('description', 'string'),
                format='%(description)s')

db.define_table('download',
                Field('title', unique=True),
                Field('file', 'upload'),
                Field('description', 'text'),
                Field('version', 'string', default='1'),
                format='%(title)s')

db.download.title.requires = IS_NOT_IN_DB(db, db.download.title)

db.define_table('scoring',
                Field('level', 'integer'),
                Field('right', 'integer'),
                Field('wrong', 'integer'),
                Field('rightchallenge', 'integer'),
                Field('wrongchallenge', 'integer'),
                Field('rightaction', 'integer'),
                Field('wrongaction', 'integer'),
                Field('nextlevel', 'integer'),
                Field('submitter', 'integer'),
                format='%(level)')

# location table is a holder for a group of events - it may be a physical place
# or virtual
db.define_table('location',
                Field('location_name', label='Location Name', requires=[not_empty, IS_SLUG(),
                                                                        IS_NOT_IN_DB(db, 'location.location_name')]),
                Field('address1', label='Address 1', writable=False, readable=False),
                Field('address2', label='Address 2', writable=False, readable=False),
                Field('address3', label='Address 3', writable=False, readable=False),
                Field('address4', label='Address 4', writable=False, readable=False),
                Field('addrcode', label='Postal Code', writable=False, readable=False),
                Field('addrurl', label='Location Website'),
                Field('continent', default='Unspecified', label='Continent'),
                Field('country', default='Unspecified', label='Country'),
                Field('subdivision', default='Unspecified', label='Subdivision'),
                Field('geox', 'double', default=0.0, label='Longitude', writable=False, readable=False),
                Field('geoy', 'double', default=0.0, label='Latitude', writable=False, readable=False),
                Field('description', 'text'),
                Field('shared', 'boolean', default=False, comment='Allows other users to link events'),
                Field('auth_userid', 'reference auth_user', writable=False, readable=False, default=auth.user_id),
                Field('createdate', 'datetime', default=request.utcnow, writable=False, readable=False),
                format='%(location_name)s')

db.location.addrurl.requires = IS_EMPTY_OR(IS_URL())

db.define_table('resolvemethod',
                Field('resolve_name','string', default='Standard', label='Name',
                      requires=[not_empty, IS_SLUG(), IS_NOT_IN_DB(db, 'resolvemethod.resolve_name')]),
                Field('description','text', default='Explain how the resolution method works',
                      label='Description of resolution method'),
                Field('method','string', default='Network', requires=IS_IN_SET(['Network','VoteVolume','VoteTime'])),
                Field('responses','integer', default=3, label='Number of Responses before evaluation'),
                Field('consensus','double', default=100, label='Percentage Agmt required to resolve'),
                Field('userselect','boolean', default=True, label='Allow users to select to answer'),
                Field('adminresolve','boolean', default=True, label='Allow event owners to resolve on behalf of group'),
                format='%(resolve_name)s')

INIT = db(db.init).select().first()
PARAMS = db(db.website_parameters).select().first()

if PARAMS:
    labeltoplevel= PARAMS.level1desc or 'TestlateContinent'


if INIT is None or INIT.website_init is False:
    if db(db.location.location_name == "Unspecified").isempty():
        locid = db.location.insert(location_name="Unspecified", shared=True)
    if db(db.continent.continent_name == "Unspecified").isempty():
        contid = db.continent.insert(continent_name="Unspecified")
    if db(db.resolvemethod.resolve_name == "Standard").isempty():
        resolveid = db.resolvemethod.insert(resolve_name="Standard")


settings.scopes = ['1 Global', '2 Continental', '3 National', '4 Local']

# , cache=(cache.ram,3600)

db.define_table('event',
                Field('event_name', label='Event Name', requires=[not_empty, IS_SLUG(),
                        IS_NOT_IN_DB(db, 'event.event_name')]),
                Field('locationid', 'reference location', label='Location'),
                Field('eventurl', label='Location Website'),
                Field('status', 'string', default='Open',
                requires=IS_IN_SET(['Open', 'Archiving', 'Archived'])),
                Field('answer_group', 'string', default='Unspecified', label='Restrict Event to Group'),
                Field('startdatetime', 'datetime', label='Start Date Time',
                      default=(request.utcnow + datetime.timedelta(days=10))),
                Field('enddatetime', 'datetime', label='End Date Time',
                      default=(request.utcnow + datetime.timedelta(days=11))),
                Field('description', 'text'),
                Field('shared', 'boolean', default=False, comment='Allows other users to link questions'),
                Field('owner', 'reference auth_user', writable=False, readable=False, default=auth.user_id,
                      label='Owner'),
                Field('createdate', 'datetime', default=request.utcnow, writable=False, readable=False),
                format='%(event_name)s')

db.event.eventurl.requires = IS_EMPTY_OR(IS_URL())
db.event.startdatetime.requires = IS_DATETIME_IN_RANGE(format=T('%Y-%m-%d %H:%M:%S'),
                                                       minimum=datetime.datetime(2014, 6, 15, 00, 00),
                                                       maximum=datetime.datetime(2021, 12, 31, 23, 59),
                                                       error_message='must be YYYY-MM-DD HH:MM::SS!')
db.event.enddatetime.requires = IS_DATETIME_IN_RANGE(format=T('%Y-%m-%d %H:%M:%S'),
                                                     minimum=datetime.datetime(2014, 6, 15, 00, 00),
                                                     maximum=datetime.datetime(2021, 12, 31, 23, 59),
                                                     error_message='must be YYYY-MM-DD HH:MM::SS!')

if INIT is None or INIT.website_init is False:
    if db(db.event.event_name == "Unspecified").isempty():
        locid = db(db.location.location_name == 'Unspecified').select(db.location.id).first().id
        evid = db.event.insert(event_name="Unspecified", locationid=locid, shared=True,
                               startdatetime=request.utcnow - datetime.timedelta(days=10),
                               enddatetime=request.utcnow - datetime.timedelta(days=9))
# configure email
mail = auth.settings.mailer
mail.settings.server = 'gae'
mail.settings.sender = 'newglobalstrategy@gmail.com'
# mail.settings.login = 'username:password'

filename = 'private/emaillogin.key'
path = os.path.join(request.folder, filename)

if os.path.exists(path):
    mail.settings.login = open(path, 'r').read().strip()

mail = None


def userinit():
    """
    This initialises user variables into the session. These are used to save
    settings for view and the likes ie short term storage of defaults without
    changing the auth values
    """
    session.userid = auth.user
    session.continent = auth.user.continent
    session.country = auth.user.country
    session.subdivision = auth.user.subdivision
    session.level = auth.user.level
    return


# setup session variables for the user if logged in and not setup
# probably these should be elsewhere but lets leave here for now
if session.userinit is None and auth.user:
    # establish session variables for user
    userinit()
    session.userinit = True
