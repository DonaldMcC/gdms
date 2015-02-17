# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

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

response.logo = IMG(_src=URL('static', 'images/ndslogosml.png'), _class="img-thumbnail img-responsive hidden-lg-inline",
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
    ('Home', False, URL('default', 'index'),
     [('Search', False, URL('search', 'newsearch')),
      ('GAE Simple Search', False, URL('search', 'gae_simple_search'))]),
    ('Create', False, URL('submit', 'new_question', args=['quest']),
     [('Create Location', False, URL('location', 'new_location')),
      ('Create Event', False, URL('event', 'new_event')),
      ('Create Group', False, URL('accessgroups', 'new_group')),
      ('Create Issue', False, URL('submit', 'new_question', args=['issue'])),
      ('Create Draft Question', False, URL('submit', 'new_question', args=['quest', 'draft'])),
      ('Create Question', False, URL('submit', 'new_question', args=['quest'])),
      ('Create Action', False, URL('submit', 'new_question', args=['action'])),
      ('Create Draft Action', False, URL('submit', 'new_question', args=['action','draft']))]),
    ('Answer', False, URL('answer', 'get_question'),
     [('Approve Issues', False, URL('answer', 'get_question', args=['issue'])),
     ('Answer Questions', False, URL('answer', 'get_question', args=['quest'])),
     ('Approve Actions', False, URL('answer', 'get_question', args=['action']))]),
    ('Review', False, URL('review', 'index'),
     [('Events', False, URL('event', 'index')),
      ('Groups', False, URL('accessgroups', 'index')),
      ('Proposed Issues', False, URL('review', 'index', args=['action', 'proposed', 'priority', 0])),
      ('Resolved Questions', False, URL('review', 'index', args=['quest', 'resolved', 'priority', 0])),
      ('Agreed Actions', False, URL('review', 'index', args=['action', 'agreed', 'priority', 0])),
      ('Proposed Actions', False, URL('review', 'index', args=['action', 'proposed', 'priority', 0])),
      ('Locations', False, URL('location', 'index'))]),
    ('My NDS', False, URL('review', 'index', args=['action']),
     [('My Issues', False, URL('review', 'index', args=['issue', 'my'])),
      ('My Questions', False, URL('review', 'index', args=['quest', 'my'])),
      ('My Actions', False, URL('review', 'index', args=['action', 'my'])),
      ('My Answers', False, URL('review', 'my_answers')),
      ('My Locations', False, URL('location', 'my_locations')),
      ('My Events', False, URL('event', 'my_events'))]),
    ('About', False, URL('about', 'index'), [
        ('FAQ', False, URL('about', 'faq')),
        ('Press Release', False, URL('about', 'pr')),
        ('Std Messages', False, URL('about', 'stdmsg')),
        ('Enhancements', False, URL('about', 'enhance')),
        ('Privacy Policy', False, URL('about', 'privacy')),
        ('Downloads', False, URL('about', 'download'))])
]

if auth.has_membership('manager'): # removed as unnecessary query every time
    response.menu += [
        (T('Admin'), False, URL('admin', 'index'), [('Appadmin', False, URL('appadmin', 'manage', args=['auth']))])]
