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
# This is the main model definition file changes should be agonised over

import datetime
from plugin_hradio_widget import hradio_widget, hcheck_widget
from plugin_range_widget import range_widget
from plugin_haystack import Haystack, SimpleBackend, GAEBackend
from ndsfunctions import getindex

not_empty = IS_NOT_EMPTY()

# is slug, is lower is not in db(db,category.name)
# need to sort out groups and categories as lowercase
# numanswers needs to be removed from this - only used on submit
#                Field('questcounts','list:integer',default=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# Field('questcounts','list:integer',default=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],

db.define_table('questcount',
                Field('groupcat','string', requires=IS_IN_SET(('C','G'))),
                Field('groupcatname','string'),
                Field('questcounts','list:integer',default=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                comment='Draft, In Prog, Resolved, Agreed, Disagreed, Rejected 3 times for Issues,'
                        ' Questions and Actions'))

# resolve method will move to reference shortly once field is populated

db.define_table('question',
                Field('qtype', 'string', writable=False,
                      requires=IS_IN_SET(['quest', 'action', 'issue']), default='quest'),
                Field('questiontext', 'text', label='Question', requires=not_empty),
                Field('level', 'integer', default=1, writable=False),
                Field('status', 'string', default='In Progress',
                      requires=IS_IN_SET(['Draft', 'In Progress', 'Resolved', 'Agreed', 'Disagreed', 'Rejected']),
                      comment='Select draft to defer for later editing'),
                Field('auth_userid', 'reference auth_user', writable=False, label='Submitter', default=auth.user_id),
                Field('category', 'string', default='Unspecified', label='Category',
                      comment='Optional', readable=settings.usecategory, writable=settings.usecategory),
                Field('answer_group', 'string', default='Unspecified', label='Submit to Group',
                      comment='Restrict answers to members of a group'),
                Field('activescope', 'string', default='1 Global', label='Active Scope',
                      requires=IS_IN_SET(settings.scopes)),
                Field('continent', 'string', default='Unspecified', label=labeltoplevel),
                Field('country', 'string', default='Unspecified', label='Country'),
                Field('subdivision', 'string', default='Unspecified', label='Sub-division eg State'),
                Field('scopetext', compute=lambda row: (row.activescope == '1 Global' and row.activescope) or
                                (row.activescope == '2 Continenal' and row.continent) or (row.activescope ==
                                '3 National' and row.country) or row.subdivision),
                Field('answers', 'list:string'),
                Field('answercounts', 'list:integer'),
                Field('correctans', 'integer', default=-1, writable=False, label='Correct Ans'),
                Field('urgency', 'decimal(6,2)', default=5, writable=False, label='Urgency'),
                Field('importance', 'decimal(6,2)', default=5, writable=False, label='Importance'),
                Field('totratings', 'integer', default=0, writable=False, label='what is this'),
                Field('priority', 'decimal(6,2)', compute=lambda r: r['urgency'] * r['importance'], writable=False,
                      label='Priority'),
                Field('othercounts', 'list:integer', default=[0, 0, 0, 0, 0, 0], readable=False, writable=False,
                      comment='numpass, numchallenges, numchallenged, numagree, numdisagree, numcomments'),
                Field('testcounts', 'list:integer'),
                Field('resolvemethod', 'string', default='Standard', label='Resolution Method'),
                Field('unpanswers', 'integer', default=0, writable=False, readable=False),
                Field('createdate', 'datetime', writable=False, label='Date Submitted', default=request.utcnow),
                Field('resolvedate', 'datetime', writable=False, label='Date Resolved'),
                Field('challengedate', 'datetime', writable=False, label='Date Challenged'),
                Field('answerreasons', 'text', writable=False, label='Reason1'),
                Field('answerreason2', 'text', writable=False, label='Reason2'),
                Field('answerreason3', 'text', writable=False, label='Reason3'),
                Field('duedate', 'datetime', label='Expiry Date', 
                       default=(request.utcnow + datetime.timedelta(days=14)),
                       comment='This only applies to items resolved by vote'),
                Field('eventid', 'reference event', label='Event'),
                Field('challenge', 'boolean', default=False))

db.question.totanswers = Field.Lazy(lambda row: sum(row.question.answercounts))
db.question.numanswers = Field.Lazy(lambda row: len(row.question.numanswers))
db.question.correctanstext = Field.Lazy(lambda row: (row.question.correctans > -1 and row.question.answers[row.question.correctans]) or '')

db.question._after_insert.append(lambda fields, id: questcount_insert(fields, id))
db.question._after_insert.append(lambda fields, id: eventmap_insert(fields, id))

def questcount_insert(fields, id):
    """
    :param fields: question fields
    :param id: question id
    :return: True
    This updates the questcounts table with a category record and an answer group record for each questio submitted
    """

    groupcat = 'G'
    #print 'call', fields['qtype'], fields['status']
    countindex = getindex(fields['qtype'], fields['status'])
    grouprow = db((db.questcount.groupcatname == fields['answer_group']) & (db.questcount.groupcat == groupcat)
                ).select().first()
    if grouprow is None:
        createcount = ['0'] * 18
        print countindex
        createcount[countindex]=1
        db.questcount.insert(groupcat=groupcat, groupcatname=fields['answer_group'], questcounts=createcount)
    else:
        updatecount=grouprow.questcounts
        print countindex,'upd',updatecount
        updatecount[countindex] += 1
        grouprow.update_record(questcounts=updatecount)
    # insert the category record
    groupcat = 'C'
    existrow = db((db.questcount.groupcatname == fields['category']) & (db.questcount.groupcat == groupcat)
                ).select().first()
    if existrow is None:
        createcount = ['0'] * 18
        createcount.append(1)
        createcount[countindex]=1
        db.questcount.insert(groupcat=groupcat, groupcatname=fields['category'], questcounts=createcount)
    else:
        updatecount=existrow.questcounts
        updatecount[countindex] += 1
        existrow.update_record(questcounts=updatecount)
    return

def eventmap_insert(fields, id):
    # this should update if event exists and is not archived
    existmap = db((db.eventmap.eventid == fields['eventid']) & (db.eventmap.status == 'Open')).select().first()
    if existmap:
        recid = db.eventmap.insert(eventid=fields['eventid'], questid=id, xpos=50, ypos=40,
                questiontext=fields['questiontext'], answers=fields['answers'], qtype=fields['qtype'],
                urgency=fields['urgency'], importance=fields['importance'], answer_group=fields['answer_group'],
                correctans=fields['correctans'], queststatus=fields['status'])
    return



#db.question.activescope.requires = IS_IN_SET(settings.scopes)
db.question.duedate.requires = IS_DATETIME_IN_RANGE(format=T('%Y-%m-%d %H:%M:%S'),
                                                    minimum=datetime.datetime(2013, 1, 1, 10, 30),
                                                    maximum=datetime.datetime(2030, 12, 31, 11, 45),
                                                    error_message='must be YYYY-MM-DD HH:MM::SS!')

if request.env.web2py_runtime_gae:
    indsearch = Haystack(db.question, backend=GAEBackend, fieldtypes=('string','text','datetime','date','list:string'))  # table to be indexed
    indsearch.indexes('questiontext', 'answers', 'category', 'continent', 'country', 'subdivision',
                      'createdate','activescope','qtype','status')
else:
    indsearch = Haystack(db.question)
    indsearch.indexes('questiontext','category')


#This table holds records for normal question answers and also for answering
#challenges and actions - in fact no obvious reason to differentiate
#the question will hold a flag to determine if under challenge but only so 
#that the challengers get credit when resolved again if the answer is 
#different

db.define_table('userquestion',
                Field('questionid', db.question, writable=False),
                Field('auth_userid', 'reference auth_user', writable=False, readable=False),
                Field('status', 'string', default='In Progress', writable=False, readable=False),
                Field('level', 'integer', readable=False, writable=False, comment='Level'),
                Field('answer', 'integer', default=0, label='My Answer'),
                Field('reject', 'boolean', default=False),
                Field('urgency', 'integer', default=5, requires=IS_INT_IN_RANGE(1, 10,
                       error_message='Must be between 1 and 10'), widget=range_widget),
                Field('importance', 'integer', default=5, requires=IS_INT_IN_RANGE(1, 10,
                       error_message='Must be between 1 and 10'), widget=range_widget),
                Field('score', 'integer', default=0, writable='False'),
                Field('answerreason', 'text', label='Reasoning'),
                Field('ansdate', 'datetime', default=request.now, writable=False, readable=False),
                Field('category', 'string', default='Unspecified'),
                Field('activescope', 'string', default='1 Global', requires = IS_IN_SET(settings.scopes)),
                Field('continent', 'string', default='Unspecified', label='Continent'),
                Field('country', 'string', default='Unspecified', label='Country'),
                Field('subdivision', 'string', default='Unspecified', label='Sub-division'),
                Field('changecat', 'boolean', default=False, label='Change Category'),
                Field('changescope', 'boolean', default=False, label='Change Scope'),
                Field('resolvedate', 'datetime', writable=False, label='Date Resolved'))

#db.userquestion.activescope.requires = IS_IN_SET(settings.scopes)

#suggest using this to stop unnecessary indices on gae but doesn't work elsewhere so need to fix somehow
#,custom_qualifier={'indexed':False} think - retry this later
#db.table.field.extra = {} looks to be the way to do this in an if gae block

db.define_table('questchallenge',
                Field('questionid', 'reference question', writable=False, readable=False),
                Field('auth_userid', 'reference auth_user', writable=False, readable=False),
                Field('status', 'string', default='In Progress', writable=False, readable=False),
                Field('challengereason', 'text'),
                Field('challengedate', 'datetime', default=request.now, writable=False, readable=False))


#this holds details of who has agreed and disagreed on the answer to a question
#no points are awarded for this at present but it may be configured to prevent
#challenges if the agreement to disagreement ratio is above some point this will also 
#now support logging agreement to actions and so urgency and importance have been 
#added to this table - however they are also picked up in userquestion - thinking is
#questions will not show this but actions will ie will pick-up in one place only
#Some users may want to record agreement without ranking immediately - but will
#accept their default values for now as no way of knowing if intended or not

db.define_table('questagreement',
                Field('questionid', 'reference question', writable=False),
                Field('auth_userid', 'reference auth_user', writable=False),
                Field('agree', 'integer', writable=False, readable=False),
                Field('agreedate', 'datetime', default=request.now, writable=False, readable=False),
                Field('urgency', 'integer', default=0, requires=IS_IN_SET([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])),
                Field('importance', 'integer', default=0, requires=IS_IN_SET([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])),
                Field('level', 'integer', default=1, readable=False, writable=False))

db.define_table('questurgency',
                Field('questionid', 'reference question', writable=False),
                Field('auth_userid', 'reference auth_user', writable=False),
                Field('urgency', 'integer', default=5, requires=IS_IN_SET([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])),
                Field('importance', 'integer', default=5, requires=IS_IN_SET([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])),
                Field('level', 'integer', default=1, readable=False, writable=False))


#questlinks replaces priorquests and subsquests in the questtion table at present as
#list reference fields weren't going to be enough to provide funcionality to 
#allow creation and deletion of links I now think the record gets deleted
#when delete count exceeds createcount and deletecount is also greater than one
#so that may mean that status can be a computed field but would need to be queried on
#so not a virtual field

db.define_table('questlink',
                Field('sourceid', 'reference question'),
                Field('targetid', 'reference question'),
                Field('createdby', 'reference auth_user', default=auth.user_id),
                Field('createcount', 'integer', default=1),
                Field('deletecount', 'integer', default=0),
                Field('status', 'string', default='Active', requires=IS_IN_SET(['Draft', 'Active', 'Rejected'])),
                Field('lastdeleter', 'reference auth_user'),
                Field('lastaction', 'string', default='create'),
                Field('createdate', 'datetime', default=request.utcnow, writable=False, readable=False))

#this holds comments for resolved questions
#it may be extended to allow comments against unresolved but not yet
#it will allow comments against actions that are proposed
#which is now a new status on actions where preceding question is not resolved
#and on follow-up questions

db.define_table('questcomment',
                Field('questionid', 'reference question', writable=False, readable=False,
                      default=session.questid),
                Field('auth_userid', 'reference auth_user', writable=False, readable=False,
                      default=auth.user_id),
                Field('comment', 'text', requires=IS_NOT_EMPTY()),
                Field('status', 'string', default='OK', writable=False, readable=False,
                      requires=IS_IN_SET(['OK', 'NOK'])),
                Field('numreject', 'integer', default=0, writable=False, readable=False),
                Field('usersreject', 'list:integer', writable=False, readable=False),
                Field('commentdate', 'datetime', default=request.utcnow, writable=False, readable=False))

#This table is never populated but holds settings and options for configuring
#many of the displays of actions and questions

db.define_table('viewscope',
                Field('sortorder', 'string', default='1 Priority', label='Sort Order'),
                Field('showscope', 'boolean', label='Show scope Filter', comment='Uncheck to show all'),
                Field('filters', 'string'),
                Field('scope', 'string', default='1 Global'),
                Field('continent', 'string', default='Unspecified', label='Continent'),
                Field('country', 'string', default='Unspecified', label='Country'),
                Field('subdivision', 'string', default='Unspecified', label='Sub-division'),
                Field('showcat', 'boolean', label='Show Category Filter', comment='Uncheck to show all'),
                Field('category', 'string', default='Unspecified', label='Category', comment='Optional'),
                Field('selection','string', default=['Issue','Question','Action','Resolved']),
                Field('answer_group', 'string', default='Unspecified', label='Answer Group'),
                Field('searchstring', 'string', label='Search string'))

db.viewscope.scope.requires = IS_IN_SET(settings.scopes)
db.viewscope.sortorder.requires = IS_IN_SET(['1 Priority', '2 Resolved Date', '3 Submit Date', '4 Answer Date'])
db.viewscope.selection.requires = IS_IN_SET(['Issue','Question','Action','Proposed','Resolved','Draft'], multiple=True)
db.viewscope.selection.widget = hcheck_widget
db.viewscope.filters.requires = IS_IN_SET(['Scope','Category','AnswerGroup'], multiple=True)
db.viewscope.filters.widget = hcheck_widget

#db.viewscope.selection.widget = SQLFORM.widgets.checkboxes.widget
db.viewscope.scope.widget = hradio_widget
db.viewscope.sortorder.widget = hradio_widget
#db.viewscope.sortorder.widget = SQLFORM.widgets.radio.widget
db.viewscope.searchstring.requires = IS_NOT_EMPTY()

#This contains two standard messages one for general objective and a second
#for specific action which someone is responsible for
db.define_table('message', Field('msgtype', 'string'),
                Field('description', 'text'),
                Field('message_text', 'text'))

db.define_table('eventmap',
    Field('eventid', 'reference event'),
    Field('questid', 'reference question'),
    Field('xpos', 'double', default=0.0, label='xcoord'),
    Field('ypos', 'double', default=0.0, label='ycoord'),
    Field('qtype', 'string', writable=False, requires=IS_IN_SET(['quest', 'action', 'issue'])),
    Field('status', 'string', default='In Progress', requires=IS_IN_SET(['Open', 'Archiving', 'Archived'])),
    Field('questiontext', 'text',  writable=False, label='Question'),
    Field('answers', 'list:string', writable=False),
    Field('correctans', 'integer', default=-1, label='Correct Ans'),
    Field('answer_group', 'string', default='Unspecified', label='Submit to Group',
                      comment='Restrict answers to members of a group'),
    Field('urgency', 'decimal(6,2)', default=5, writable=False, label='Urgency'),
    Field('importance', 'decimal(6,2)', default=5, writable=False, label='Importance'),
    Field('priority', 'decimal(6,2)', compute=lambda r: r['urgency'] * r['importance'], writable=False,
                      label='Priority'),
    Field('auth_userid', 'reference auth_user', writable=False, label='Submitter', default=auth.user_id),
    Field('adminresolve', 'boolean', default=False, label='True if answer or status adjusted by event owner' ),
    Field('queststatus', 'string', default='In Progress',
          requires=IS_IN_SET(['Draft', 'In Progress', 'Resolved', 'Agreed', 'Disagreed', 'Rejected', 'Admin Resolved']),
          comment='Select draft to defer for later editing'))

db.eventmap.correctanstext = Field.Lazy(lambda row: (row.eventmap.correctans > -1 and row.eventmap.answers[row.eventmap.correctans]) or '')


# This is for inserting queue items for scoring of quick responses to actions and issues for now - think 
# this will be a straight routing from Ajax for those questions
# hoping to not need this as processing in real time seems better

#db.define_table('qscorequest',
#    Field('questid', 'integer'),
#    Field('status', 'string', default='new'),
#    Field('createdate', 'datetime', writable=False, label='Date Submitted', default=request.utcnow),
#    Field('processdate', 'datetime', writable=False, label='Date Processed'))
    

#This caching doesnt appear to work
#if (not INIT) or INIT.website_init is False:
#if (not INIT) or INIT.website_init is False:
#no caching until this is true - this doesnt appear to work when we switch back to the cached one we get nothing again
#and user registration fails on continent only
#db.person.name.requires = IS_IN_DB(db(db.person.id>10), 'person.id', '%(name)s')

#db.define_table('group_members',
#                Field('access_group', 'reference access_group'),
#                Field('auth_userid', 'reference auth_user'))


db.auth_user.exclude_categories.requires = IS_EMPTY_OR(IS_IN_DB(db, 'category.cat_desc', multiple=True))
db.question.category.requires = IS_IN_DB(db, 'category.cat_desc')
db.question.resolvemethod.requires = IS_IN_DB(db, 'resolvemethod.resolve_name')
#db.question.answer_group.requires = IS_IN_DB(db(db.group_members==auth.user_id), 'access_group', '%(group_name)s')

#subset=db(db.group_members.auth_userid==auth.user_id)
#db.question.answer_group.requires = IS_IN_DB(db(db.access_group.id>0), 'access_group.id', '%(group_name)s',
#                                            _and=IS_IN_DB(subset, 'group_members.access_group'))

db.auth_user.continent.requires = IS_IN_DB(db, 'continent.continent_name')
db.question.continent.requires = IS_IN_DB(db, 'continent.continent_name')
db.location.continent.requires = IS_IN_DB(db, 'continent.continent_name')
db.viewscope.category.requires = IS_IN_DB(db, 'category.cat_desc')
db.viewscope.continent.requires = IS_IN_DB(db, 'continent.continent_name')
db.userquestion.category.requires = IS_IN_DB(db, 'category.cat_desc')
db.userquestion.continent.requires = IS_IN_DB(db, 'continent.continent_name')
#else:
#    db.auth_user.exclude_categories.requires = IS_EMPTY_OR(IS_IN_DB(db, 'category.cat_desc', cache=(cache.ram,3600), multiple=True))
#    db.question.category.requires = IS_IN_DB(db, 'category.cat_desc', cache=(cache.ram,3600))
#    db.auth_user.continent.requires = IS_IN_DB(db, 'continent.continent_name', cache=(cache.ram,3600))
#    db.question.continent.requires = IS_IN_DB(db, 'continent.continent_name', cache=(cache.ram,3600))
#    db.location.continent.requires = IS_IN_DB(db, 'continent.continent_name', cache=(cache.ram,3600))
#    db.viewscope.category.requires = IS_IN_DB(db, 'category.cat_desc', cache=(cache.ram,3600))
#    db.viewscope.continent.requires = IS_IN_DB(db, 'continent.continent_name', cache=(cache.ram,3600))
#    db.userquestion.category.requires = IS_IN_DB(db, 'category.cat_desc', cache=(cache.ram,3600))
#    db.userquestion.continent.requires = IS_IN_DB(db, 'continent.continent_name', cache=(cache.ram,3600))


#need to figure out how I am storing the shape date - not currently using
db.define_table('shape_template',
                Field('shape_type', 'string'),
                Field('shape_prefix', 'string', comment='Three character prefix for ids created with this shape'),
                Field('shape_json', 'text'),
                Field('description', 'text'),
                Field('cub_action', 'text'))


