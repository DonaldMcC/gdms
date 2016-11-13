# -*- coding: utf-8 -*-
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

# ########################################################################
# Customize your APP title, subtitle and menus here
# #######################################################################
response.title = request.application.replace('_', ' ').title()
# response.title = ' '.join(word.capitalize() for word in request.application.split('_'))
# response.subtitle = T('A whole new paradigm for decision making')

# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# #######################################################################
#  Customize your APP title, subtitle and menus here
# #######################################################################


response.logo = IMG(_src=URL('static', 'images/ndslogo.svg'), _class="img-thumbnail img-responsive visible-lg-inline",
                    _alt="NDS Logo")

# read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Russ King <newglobalstrategy@gmail.com>'
response.meta.description = 'Network Decision Making'
response.meta.keywords = 'web2py, python, framework, global, decision-making'
response.meta.generator = 'Web2py Web Framework, Networked Decision Making'
response.meta.copyright = 'Has been phased out on more advanced planets'

# your http://google.com/analytics id
response.google_analytics_id = None

# #######################################################################
# # this is the main application menu add/remove items as required
# #######################################################################
#  [('Search', False, URL('search', 'index'))]),


response.menu = [
    ('About', False, '#',
     [('Home', False, URL('default', 'index')),
      ('Search', False, URL('search', 'newsearch')),
      ('About NDS', False, URL('about', 'index')),
      ('FAQ', False, URL('about', 'faq')),
      ('Presentation', False, URL('about', 'present')),
      ('Enhancements', False, URL('about', 'enhance')),
      ('Privacy Policy', False, URL('about', 'privacy')),
      ('Downloads', False, URL('about', 'download'))]),
      ('Create', False, '#',
     [('Create Location', False, URL('location', 'new_location')),
      ('Create Project', False, URL('project', 'new_project')),
      ('Create Event', False, URL('event', 'new_event')),
      ('Create Group', False, URL('accessgroups', 'new_group')),
      ('Create Issue', False, URL('submit', 'new_question', args=['issue'])),
      ('Create Question', False, URL('submit', 'new_question', args=['quest'])),
      ('Create Action', False, URL('submit', 'new_question', args=['action']))]),
      ('Answer', False, '#',
      [('Approve Issues', False, URL('answer', 'get_question', args=['issue'])),
      ('Answer Questions', False, URL('answer', 'get_question', args=['quest'])),
      ('Approve Actions', False, URL('answer', 'get_question', args=['action']))]),
      ('Review', False, '#',
      [('Locations', False, URL('location', 'index')),
      ('Projects', False, URL('project', 'index')),
      ('Events', False, URL('event', 'index')),
      ('Groups', False, URL('accessgroups', 'index')),
      ('Issues', False, URL('review', 'newindex', args=['issue', 'InProg', 'priority', 0, 'Yes'])),
      ('Questions', False, URL('review', 'newindex', args=['quest', 'resolved', 'priority', 0, 'Yes'])),
      ('Actions', False, URL('review', 'newindex', args=['action', 'agreed', 'priority', 0, 'Yes'])),
      ('Proposals', False, URL('review', 'newindex', args=['action', 'InProg', 'priority', 0, 'Yes'])),
      ('Resolved', False, URL('review', 'newindex', args=['quest', 'resolved', 'priority', 0, 'Yes'])),
      ('Activity', False, URL('review', 'newindex', args=['activity']))
     ]),
     ('Plan', False, '#',
      [('Actions', False, URL('review', 'newindex', args=['plan', 'agreed', 'priority', 0])),
      ('Gantt', False, URL('gantt', 'index', args=['plan', 'agreed', 'priority', 0, 'Yes']))
     ]),
    ('My NDS', False, '#',
     [('My Issues', False, URL('review', 'newindex', args=['issue', 'my'])),
      ('My Questions', False, URL('review', 'newindex', args=['quest', 'my'])),
      ('My Draft Items', False, URL('review', 'newindex', args=['items', 'Draft'])),
      ('My Actions', False, URL('review', 'newindex', args=['action', 'my'])),
      ('My Answers', False, URL('review', 'my_answers')),
      ('My Locations', False, URL('location', 'my_locations')),
      ('My Events', False, URL('event', 'my_events')),
      ('My Projects', False, URL('project', 'my_projects'))]),
]


if auth.has_membership('manager'): 
    response.menu += [
        (T('Admin'), False, '#', [(T('Admin'), False, URL('admin', 'index')),
                                  (T('Upgrade'), False, URL('upgrade', 'index')),
                                  ('Appadmin', False, URL('appadmin', 'manage', args=['auth']))])]
