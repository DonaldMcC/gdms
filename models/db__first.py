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
#
# This file in particular borrows heavily from web2py appliance tiny website
#########################################################################
# Things to be initialized before main model

import datetime
from plugin_bs_datepicker import bsdatepicker_widget, bsdatetimepicker_widget

not_empty = IS_NOT_EMPTY()

db.define_table('initialised',
                Field('website_init', 'boolean', default=False))

db.define_table('resolve',
                Field('resolve_name', 'string', default='Standard', label='Name',
                      requires=[not_empty, IS_SLUG(), IS_NOT_IN_DB(db, 'resolve.resolve_name')]),
                Field('description', 'text', default='Explain how the resolution method works',
                      label='Description of resolution method'),
                Field('resolve_method', 'string', default='Network', requires=IS_IN_SET(['Network', 'Vote'])),
                Field('responses', 'integer', default=3, label='Number of Responses before evaluation'),
                Field('consensus', 'double', default=100, label='Percentage Agmt required to resolve'),
                Field('userselect', 'boolean', default=True, label='Allow users to select to answer'),
                Field('adminresolve', 'boolean', default=True,
                      label='Allow event owners to resolve on behalf of group'),
                format='%(resolve_name)s')

db.define_table('website_parameters',
                Field('website_name', label=T('Website name'), comment=T('Not currently used')),
                Field('website_init', 'boolean', default=False, label=T('Website Setup'),
                      comment=T('Set to True once initialised')),
                Field('website_title', label=T('Website title'), comment=T('Displayed in title if not blank')),
                Field('website_subtitle', label=T('Website subtitle'), comment=T('Not used')),
                Field('website_url', label=T('Url'), comment=T('URL of the website used for emailing external links')),
                Field('longdesc', 'text', label=T('Long Description'), comment=T('Subject of the website')),
                Field('shortdesc', label=T('Url'), comment=T('Short Description of the website')),
                Field('level1desc', label=T('Level1Desc'), comment=T('First Location Level')),
                Field('level2desc', label=T('Level2Desc'), comment=T('Second Location Level')),
                Field('level3desc', label=T('Level3Desc'), comment=T('Third Location Level')),
                Field('del_answers',  'boolean', default=False, label=T('Delete User Answer on Resolution - not used')),
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
                Field('quests_per_page', 'integer', default=20, label=T('Questions Per Page'),
                      comment=T('Port of the mailserver (used to send email in forms)')),
                Field('comments_per_page', 'integer', default=20, label=T('Comments Per Page'),
                      comment=T('Port of the mailserver (used to send email in forms)')),
                Field('default_resolve_name', 'string', default='Standard', label='Default Resolve Name'))

db.website_parameters.website_url.requires = IS_EMPTY_OR(IS_URL())
db.website_parameters.default_resolve_name.requires = IS_EMPTY_OR(IS_IN_DB(db, 'resolve.resolve_name'))

db.define_table('category',
                Field('cat_desc', 'string', label='Category',
                      requires=[not_empty, IS_NOT_IN_DB(db, 'category.cat_desc'), IS_LOWER()]),
                Field('categorydesc', 'text', label='Description'),
                format='%(cat_desc)s')

# this will contain all groups setup to restrict acess to questions
db.define_table('access_group',
                Field('group_name', 'string', label='Group Name',
                      requires=[not_empty, IS_SLUG(), IS_NOT_IN_DB(db, 'access_group.group_name'), IS_LOWER()]),
                Field('group_desc', 'text', label='Description'),
                Field('group_type', 'string', default='public',
                      requires=(IS_IN_SET(['all', 'public', 'apply', 'invite', 'admin']))),
                Field('group_owner', 'reference auth_user', writable=False, readable=False, default=auth.user_id),
                Field('createdate', 'datetime', default=request.utcnow, writable=False, readable=False),
                format='%(group_name)s')

db.define_table('group_members',
                Field('access_group', 'reference access_group'),
                Field('auth_userid', 'reference auth_user'),
                Field('user_role', default='member', requires=(IS_IN_SET(['member', 'admin']))),
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
    db.group_members.insert(access_group=id, auth_userid=auth.user_id)
    return


# so for now a public group can be joined by anyone and they can be viewed with a button to join
# groups that accept applications will also be viewable and applications will go to the owner for
# approval - invites can be sent to people to confirm they want to join and admin just bascically means
# admin appoints and probalby setup the admin piece of this first and then add the user functions later

labeltoplevel = 'Region'
labelmidlevel = 'Principality'
labellowlevel = 'County'
tmplabel = 'Sub-Division eg State, Province, County'

db.define_table('continent',
                Field('continent_name', 'string', label=labeltoplevel,
                      requires=[not_empty, IS_SLUG(), IS_NOT_IN_DB(db, 'continent.continent_name')]),
                format='%(continent_name)s')

db.define_table('country',
                Field('country_name', 'string', label=labelmidlevel,
                      requires=[not_empty, IS_SLUG(), IS_NOT_IN_DB(db, 'country.country_name')]),
                Field('continent', 'string', label='Continent'),
                format='%(country_name)s')

db.define_table('subdivision',
                Field('subdiv_name', 'string', label=labellowlevel),
                Field('country', 'string'),
                format='%(subdiv_name)s')

db.define_table('system_scope',
                Field('description', 'string'),
                format='%(description)s')

db.define_table('download',
                Field('title'),
                Field('download_file', 'upload'),
                Field('description', 'text'),
                Field('download_version', 'string', default='1'),
                format='%(title)s')

db.download.title.requires = IS_NOT_IN_DB(db, db.download.title)

db.define_table('scoring',
                Field('scoring_level', 'integer'),
                Field('correct', 'integer'),
                Field('wrong', 'integer'),
                Field('rightchallenge', 'integer'),
                Field('wrongchallenge', 'integer'),
                Field('rightaction', 'integer'),
                Field('wrongaction', 'integer'),
                Field('nextlevel', 'integer'),
                Field('submitter', 'integer'))

# location table is a holder for a group of events - it may be a physical place
# or virtual
db.define_table('locn',
                Field('location_name', label='Location Name', requires=[not_empty,
                                                                        IS_NOT_IN_DB(db, 'locn.location_name')]),
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
                Field('locn_shared', 'boolean', label='Shared', default=False,
                      comment='Allows other users to link events'),
                Field('auth_userid', 'reference auth_user', writable=False, readable=False, default=auth.user_id),
                Field('createdate', 'datetime',  default=request.utcnow, writable=False, readable=False),
                format='%(location_name)s')

db.locn.addrurl.requires = IS_EMPTY_OR(IS_URL())


INIT = db(db.initialised).select().first()
PARAMS = db(db.website_parameters).select().first()

if PARAMS:
    labeltoplevel = PARAMS.level1desc or 'DfltContinent'
    labelmidlevel = PARAMS.level2desc or 'DfltCountry'
    labellowlevel = PARAMS.level3desc or 'DfltSubdivision'

if INIT is None or INIT.website_init is False:
    if db(db.continent.continent_name == "Unspecified").isempty():
        contid = db.continent.insert(continent_name="Unspecified")
    if db(db.resolve.resolve_name == "Standard").isempty():
        resolveid = db.resolve.insert(resolve_name="Standard")

scopes = ['1 Global', '2 Continental', '3 National', '4 Local']

db.define_table('evt',
                Field('evt_name', label='Event Name'),
                Field('locationid', 'reference locn', label='Location'),
                Field('eventurl', label='Event Website'),
                Field('status', 'string', default='Open',
                      requires=IS_IN_SET(['Open', 'Archiving', 'Archived'])),
                Field('answer_group', 'string', default='Unspecified', label='Restrict Event to Group'),
                Field('startdatetime', 'datetime', label='Start Date Time',
                      default=(request.utcnow + datetime.timedelta(days=10)), widget=bsdatepicker_widget()),
                Field('enddatetime', 'datetime', label='End Date Time',
                      default=(request.utcnow + datetime.timedelta(days=11)), widget=bsdatetimepicker_widget()),
                Field('description', 'text'),
                Field('evt_shared', 'boolean', default=False, label='Shared Event', comment='Allows other users to link questions'),
                Field('evt_owner', 'reference auth_user', writable=False, readable=False, default=auth.user_id,
                      label='Owner'),
                Field('createdate', 'datetime', default=request.utcnow, writable=False, readable=False),
                Field('next_evt', 'integer', default=0,  label='Next Event'),
                Field('prev_evt', 'integer',  default=0, label='Previous Event'),
                Field('recurrence', 'string', default='None',
                      requires=IS_IN_SET(['None', 'Daily', 'Weekly', 'Bi-weekly','Monthly'])),
                format='%(evt_name)s')

db.evt.eventurl.requires = IS_EMPTY_OR(IS_URL())
db.evt.startdatetime.requires = IS_DATETIME_IN_RANGE(format=T('%Y-%m-%d %H:%M:%S'),
                                                     minimum=datetime.datetime(2014, 6, 15, 00, 00),
                                                     maximum=datetime.datetime(2021, 12, 31, 23, 59),
                                                     error_message='must be YYYY-MM-DD HH:MM::SS!')
db.evt.enddatetime.requires = IS_DATETIME_IN_RANGE(format=T('%Y-%m-%d %H:%M:%S'),
                                                   minimum=datetime.datetime(2014, 6, 15, 00, 00),
                                                   maximum=datetime.datetime(2021, 12, 31, 23, 59),
                                                   error_message='must be YYYY-MM-DD HH:MM::SS!')
                                                   
db.evt.evt_name.requires=[not_empty,IS_NOT_IN_DB(db, 'evt.evt_name')]

# configure email
# not clear if this can be setup - so lets try without for now
# EMAIL_USE_TLS = True

mail = auth.settings.mailer
current.auth = auth
current.mail = mail
current.session = session
current.response = response
current.T = T

if useappconfig:
    mail.settings.server = myconf.take('smtp.server')
    mail.settings.sender = myconf.take('smtp.sender')
    mail.settings.login = myconf.take('smtp.login')
else:
    mail.settings.server = 'undefined'
    mail.settings.sender = 'undefined'
    mail.settings.login = 'undefined'

if debug:
    mail.settings.server = 'logging:emailout.html'
