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


# The first user to register gets given admin privileges
# However for now the only routing supported will be standard routing - but
# may add different numbers of participants at each layer and %age agreement
# below 100% at some stage
# probably should be a manager page of links

"""
    exposes:
    This needs fully updated but do at the end
    http://..../[app]/admin/checkquestcounts
    http://..../[app]/about/index change
    http://..../[app]/about/privacy update
    http://..../[app]/about/faq update
    http://..../[app]/about/pr update
    http://..../[app]/about/enhance remove
    http://..../[app]/about/stdmsg change in database
    http://..../[app]/about/download keep
    http://..../[app]/about/get works with download

    """

from ndsfunctions import getindex, score_question, email_setup


@auth.requires_membership('manager')
def callscorequest():
    questid = request.args(0, default='G')
    score_question(questid)

@auth.requires_membership('manager')
def emailtest():
    # This option is not on the main menu - may add another menu with checks and dashboard
    subject = 'Test Email'
    msg = 'This is a test message'
    result = send_email(mail.settings.sender, mail.settings.sender, subject, msg)
    if result is True:
        message = 'email sent'
    else:
        message = 'there was an error sending email'
    return message


@auth.requires_membership('manager')
def checkquestcounts():
    """ This will iterate through questions and count the numbers
        at each status to verify that the questcounts table is in line with the
        status of the questions we should build a dictionary of dictionaroes in general keyed on
        the id of the matching questcount record as that should make updating - if no matching 
        questcount then key will be insert1, 2, 3 etc """

    groupcat = request.args(0, default='G')
    # groupcat='G'
    quests = db(db.question.id > 0).select()
    questcountdict = {}
    
    for quest in quests:
        # if quest.answer_group == 'Unspecified':
        #    groupcat = 'C'
        #    groupcatname = quest.category
        # else:
        if groupcat == 'G':
            groupcatname = quest.answer_group
        else:
            groupcatname = quest.category

        grouprow = db((db.questcount.groupcatname == groupcatname) & (db.questcount.groupcat == groupcat)
                      ).select().first()
        # if existrows:
        #    existrow = existrows.first()
        # above will either get the id to update to insert or get the id to create

        countindex = getindex(quest.qtype, quest.status)
        if grouprow is None or not (grouprow.id in questcountdict):
            # create a new key based on index
            createcount = [0] * 18
            createcount[countindex] = 1
            # need to actually look for key in dictionary as well here I think
            if grouprow is None:
                key = 99999999
            else:
                key = grouprow.id
            questcountdict[key] = {'groupcat': groupcat,
                                   'groupcatname': groupcatname, 'questcounts': createcount, 'id': key}
        else:
            # updatecount=[existow.id]['questcounts']
            # updatecount[countindex] += 1
            # questcountdict[existow.id]['questcounts'] = updatecount
            questcountdict[grouprow.id]['questcounts'][countindex] += 1

    # above should build questcountdict

    errors = False
    errorlist = []
    for key in questcountdict:
        grouprow = db(db.questcount.id == key).select().first()
        if not grouprow:
            errors = True
            errorlist.append(['missing', questcountdict])
        else:
            # existrow = existrows.first()
            if grouprow.questcounts != questcountdict[key]['questcounts']:
                errors = True
                errorlist.append([grouprow, questcountdict[key]])

    if errors:
        message = 'Question group counts are incorrect'
    else:
        message = 'All group question counts agree'

    return dict(message=message, errors=errors, errorlist=errorlist)


@auth.requires_membership('manager')
def index():
    return locals()


@auth.requires_membership('manager')
def scoring():
    grid = SQLFORM.grid(db.scoring, orderby=[db.scoring.scoring_level])
    return dict(grid=grid)


# This allows editing of the website_parameters of the decision making system
@auth.requires_membership('manager')
def website_parameters():
    grid = SQLFORM.grid(db.website_parameters)
    return dict(grid=grid)


# This allows editing of the categories within the subject of the system
@auth.requires_membership('manager')
def category():
    grid = SQLFORM.grid(db.category)
    # form = crud.create(db.category,message='category added')
    return dict(grid=grid)


@auth.requires_membership('manager')
def mgr_questions():
    grid = SQLFORM.grid(db.question, ignore_rw=True,
                        formstyle=SQLFORM.formstyles.bootstrap3_inline)
    return locals()


@auth.requires_membership('manager')
def mgr_answers():
    grid = SQLFORM.grid(db.userquestion, ignore_rw=True, orderby=[~db.userquestion.ansdate])
    return locals()


@auth.requires_membership('manager')
def mgr_users():
    grid = SQLFORM.grid(db.auth_user, ignore_rw=True, orderby=[~db.auth_user.id])
    return locals()


@auth.requires_membership('manager')
def mgr_resolved():
    grid = SQLFORM.grid(db.question.status == 'Resolved', orderby=[~db.question.resolvedate])
    return locals()


@auth.requires_membership('manager')
def continent():
    grid = SQLFORM.grid(db.continent)
    return dict(grid=grid)


@auth.requires_membership('manager')
def country():
    grid = SQLFORM.grid(db.country)
    return dict(grid=grid)


@auth.requires_membership('manager')
def subdivision():
    grid = SQLFORM.grid(db.subdivision)
    return dict(grid=grid)

@auth.requires_membership('manager')
def messages():
    grid = SQLFORM.grid(db.app_message)
    return dict(grid=grid)
    
@auth.requires_membership('manager')
def company():
    grid = SQLFORM.grid(db.company)
    return dict(grid=grid)


@auth.requires_membership('manager')
def individual():
    grid = SQLFORM.grid(db.individual)
    return dict(grid=grid)


@auth.requires_membership('manager')
def event():
    grid = SQLFORM.grid(db.evt)
    return dict(grid=grid)


@auth.requires_membership('manager')
def access_group():
    grid = SQLFORM.grid(db.access_group)
    return dict(grid=grid)


@auth.requires_membership('manager')
def group_members():
    grid = SQLFORM.grid(db.group_members)
    return dict(grid=grid)


@auth.requires_membership('manager')
def eventmap():
    grid = SQLFORM.grid(db.eventmap)
    return dict(grid=grid)


@auth.requires_membership('manager')
def location():
    grid = SQLFORM.grid(db.locn)
    return dict(grid=grid)


@auth.requires_membership('manager')
def upload():
    grid = SQLFORM.grid(db.download)
    return dict(grid=grid)


@auth.requires_membership('manager')
def resolvemethod():
    grid = SQLFORM.grid(db.resolve)
    return dict(grid=grid)


# This allows editing of the categories within the subject of the system
@auth.requires_membership('manager')
def email_runs():
    #result=runactivity()
    #print result
    grid = SQLFORM.grid(db.email_runs)
    return dict(grid=grid)


@auth.requires_membership('manager')
def approveusers():
    users = db(db.auth_user.registration_key == 'pending').select(db.auth_user.id,
                                                                  db.auth_user.first_name, db.auth_user.last_name,
                                                                  db.auth_user.email,
                                                                  db.auth_user.registration_key)

    return dict(users=users)


@auth.requires_membership('manager')
def zeroscores():
    users = db(db.auth_user.id > 0).select(db.auth_user.id, db.auth_user.numquestions,
                                           db.auth_user.score, db.auth_user.rating, db.auth_user.level,
                                           db.auth_user.numcorrect, db.auth_user.numwrong, db.auth_user.numpassed)

    for user in users:
        user.numquestions = 0
        user.score = 0
        user.rating = 1
        user.level = 1
        user.numcorrect = 0
        user.numwrong = 0
        user.numpassed = 0
        user.update_record()

    return dict(message='All scores reset to zero')


@auth.requires_membership('manager')
def clearquests():
    db.eventmap.drop()
    db.userquestion.drop()
    db.questagreement.drop()
    db.questchallenge.drop()
    db.questcomment.drop()
    db.questcount.drop()
    db.questlink.drop()
    db.questurgency.drop()
    db.question.truncate()
    db(db.evt.evt_name != 'Unspecified').delete()
    return dict(message='All quests cleared')


@auth.requires_membership('manager')
def clearall():
    db.userquestion.drop()
    db.questagreement.drop()
    db.questurgency.drop()
    db.questlink.drop()
    db.questchallenge.drop()
    db.questcomment.drop()
    db.question.drop()
    db.evt.drop()
    db.locn.drop()
    db.viewscope.drop()
    db.subdivision.drop()
    db.country.drop()
    db.continent.drop()
    db.scoring.drop()
    # db.download.truncate()
    db.category.drop()
    db.eventmap.drop()
    db.website_parameters.drop()

    return dict(message='Entire Database excecpt auth cleared out')


@auth.requires_membership('manager')
def fullreset():
    for table_name in db.tables():
        db[table_name].drop()

    return dict(message='Everything cleared out')
@auth.requires_login()
def datasetup():
    # This now needs reworked as some of the data needs to be creaed prior to the models execution
    # and so tables won't be empty - I think approach is to add all missing data which is slow
    # but effective will pull everything and then add the missing ones

    if db(db.category.id > 0).isempty():
        db.category.insert(cat_desc="None",
                           categorydesc="Set to select all questions")
        db.category.insert(cat_desc="Unspecified",
                           categorydesc="Catchall category")

    if db(db.initialised.id > 0).isempty():
        db.initialised.insert(website_init=True)
        global INIT
        INIT = db(db.initialised).select().first()

    if db(db.website_parameters.id > 0).isempty():
        db.website_parameters.insert(website_name='NDS Test System', website_title='Net Decision Making', website_url='http://127.0.0.1:8081',
                                    longdesc='This is a test version of networked decision making', shortdesc='Test net decision making',
                                    level1desc='Contnent', level2desc='Countrie', level3desc='Area', seo_meta_author='Russ King', 
                                    seo_meta_description='Platform for group decision making without meetings')


    # setup the basic scopes that are to be in use and populate some default
    # continents, countrys and regions

    if db(db.system_scope.description == "1 Global").isempty():
        db.system_scope.insert(description="1 Global")
    if db(db.system_scope.description == "2 Continental").isempty():
        db.system_scope.insert(description="2 Continental")
    if db(db.system_scope.description == "3 National").isempty():
        db.system_scope.insert(description="3 National")
    if db(db.system_scope.description == "4 Local").isempty():
        db.system_scope.insert(description="4 Local")

    if db(db.continent.continent_name == "Unspecified").isempty():
        db.continent.insert(continent_name="Unspecified")

    if db(db.country.country_name == "Unspecified").isempty():
        db.country.insert(country_name="Unspecified", continent="Unspecified")
        
    if db(db.locn.location_name == "Unspecified").isempty():
        locid = db.locn.insert(location_name="Unspecified", locn_shared=True)
    if db(db.evt.evt_name == "Unspecified").isempty():
        locid = db(db.locn.location_name == 'Unspecified').select(db.locn.id).first().id
        evid = db.evt.insert(evt_name="Unspecified", locationid=locid, evt_shared=True,
                             startdatetime=request.utcnow - datetime.timedelta(days=10),
                             enddatetime=request.utcnow - datetime.timedelta(days=9))

    email_setup()
    schedule_email_runs()
        
    myconf.init = False
    return locals()


@auth.requires_login()
def init():
    # This function will be called to initialise the system the following
    # activities are required here
    # 1  Give the intial user manager role to admin the system
    # 2  Populate the scoring table
    # 3  Key in the subject of the database
    # 4  Provide details of how to admin the system
    # 5  Add a default category

    login = myconf.take('login.logon_methods')
    if db(db.website_parameters.id > 0).isempty():
        if useappconfig:
            google_analytics_id = myconf.take('google.analytics_id')
        else:
            google_analytics_id = None
        db.website_parameters.insert(shortdesc="This system should be used for any topic",
                                     longdesc='This system should be used for questions on any topic that '
                                              'you consider important to human progress',
                                     google_analytics_id=google_analytics_id)

    # Need to also ensure unspecified continent,region and country are present
    # think values will now be mandatory for new user registration

    #   Populate the scoring table
    scores = db(db.scoring.id > 0).select().first()

    if scores is None:
        for k in xrange(1, 30):
            db.scoring.insert(scoring_level=k, correct=k * 10, wrong=k, rightchallenge=k * 10,
                              wrongchallenge=k * -10, rightaction=k * 5, wrongaction=k,
                              nextlevel=k * k * 20, submitter=k * 10)

        db.commit()

    # Update the first user to have manager access
    # Add an auth_group record of manager if it doesn't exist

    mgr = db(db.auth_group.role == 'manager').select().first()
    if mgr is None:
        mgr = auth.add_group('manager', 'The admin group for the app')
        auth.add_membership(mgr, auth.user_id)
    if db(db.locn.location_name == "Unspecified").isempty():
        locid = db.locn.insert(location_name="Unspecified", locn_shared=True)
    if db(db.evt.evt_name == "Unspecified").isempty():
        locid = db(db.locn.location_name == 'Unspecified').select(db.locn.id).first().id
        evid = db.evt.insert(evt_name="Unspecified", locationid=locid, evt_shared=True,
                             startdatetime=request.utcnow - datetime.timedelta(days=10),
                             enddatetime=request.utcnow - datetime.timedelta(days=9))
    return locals()


@auth.requires_membership('manager')
def addstdcategories():
    categories = [["Unspecified", "Catchall category"], ["Water", "Water"],
                  ["Food", "Food"], ["Shelter", "Shelter"],
                  ["Healthcare", "Healthcare"], ["Freedom", "Freedom"], ["Fairness", "Fairness"], ["Fun", "Fun"],
                  ["Net Decision Making", "Net Decision Making"], ["Strategy", "Strategy"],
                  ["Organisation", "Organisation"], ["Education", "Education"], ["Philosophy", "Philosophy"]]

    for x in categories:
        if db(db.category.cat_desc == x[0]).isempty():
            db.category.insert(cat_desc=x[0], categorydesc=x[1])

    myconf.init = False
    return locals()


@auth.requires_membership('manager')
def addresolvemethods():
    resolvemethods = [["Standard", "Std method ", 'Network', 3, 100.0, True, True], 
                      ["Netdecision2", "Networked decision 2 users per level", 'Network', 2, 100.0, True, True],
                      ["Netdecision4", "Networked decision 4 users per level", 'Network', 4, 100.0, True, True],
                      ["NetNoSelect", "Networked decision but not allowed for users to select for answering", 'Network',
                       3, 100.0, False, True],
                      ["Single", "Single User", 'Network', 1, 100.0, True, True],
                      ["StdVote", "Std vote with a deadline for voting", 'Vote', 3, 0.0, True, True],
                      ["MajorityVote", "Std vote but requires over 50% majority to resolve - otherwise moves to "
                                       "rejected", 'Vote', 0, 50.0, True, True]]

    for x in resolvemethods:
        if db(db.resolve.resolve_name == x[0]).isempty():
            db.resolve.insert(resolve_name=x[0], description=x[1], resolve_method=x[2], responses=x[3], consensus=x[4],
                              userselect=x[5], adminresolve=x[6])

    myconf.init = False
    return locals()


@auth.requires_membership('manager')
def addstdgroups():
    access_groups = [["Unspecified", "Catchall Group", 'all' ], ["Committee", "Sample Admin Group", 'admin'],
                     ["Activists", "Sample Public Group", 'public'], ["ApplyGroup", "Sample application group", 'apply'],
                     ["InviteGroup", "Sample Invite Group", 'invite']]

    for x in access_groups:
        if db(db.access_group.group_name == x[0]).isempty():
            db.access_group.insert(group_name=x[0], group_desc=x[1], group_type=x[2])

    myconf.init = False
    return locals()


@auth.requires_membership('manager')
def stdmessages():
    stdmsg = """You have been identified as a significant global leader either through a political or corporate leadership position, or due to having significant wealth or influence within a region.
We are frustrated at the lack of progress this planet appears to be making towards providing the majority of its inhabitants with longer happier lives.
 
A key issue we have identified is the lack of an agreed global strategy and we are proposing the adoption of a short term objective of getting global life expectancy to 80 by the year 2020. This can be considered to be our 2020 vision and can also be described as a re-definition of the 80/20 rule or pareto principal with which you may already be familiar. 

We will be holding you accountable to help drive this vision forward and make an active contribution to achieving this strategy.  In our eyes you are now accountable to the planet as a whole rather than just your current stakeholders or citizens.  We will be assessing how well you align your activities with our vision and we will be sending you reports periodically advising you of how well we assess you are performing.  We will also be setting up an on-line tracking system so other people can review and comment on our assessment of your performance.

As an added incentive to your participation in our vision it is proposed that we migrate entitlement to more advanced and expensive healthcare treatments which you may require in future towards those whose behaviour is well aligned with our strategy.  The precise eligibility criteria in future will depend on resource availability but you should be clear that evidence that you have failed to align your activities with the global strategy will not be helpful to your chances of being eligible for some of the advanced treatments which may become available.

Obviously at present we lack full credibility in this mission, however we will be building this up over the coming years.  The improvements in communication technology now make global crowdsourcing of strategy for planet earth a viable activity and we will be refining the strategy as more people come on board.  Our longer term aim is very much to make dying optional/reversible as eternal life seems to be a popular global concept and it seems many people would be interested in this if we could address some of the other inequalities of life at present.  

However eternal life for all poses some challenges and so we think it’s sensible to suggest that good behaviour rather than accumulated wealth will be the correct criteria for entitlement to longevity as it is theoretically possible for everybody to be well behaved, whereas it is presently impossible for everyone to be wealthy at the same time, and the competition for wealth is arguably the greatest blight on the world today.

Your time in power will be relatively fleeting – however our objective is to establish a system that can run the world for many years to come.  It will be built on the established technologies we have today and using them to empower the best people to make decisions that are right for the planet as a whole rather than the specific benefactors most closely associated with the decision maker.

We look forward to your help in making the world a better place."""

    actmsg = """You have been identified as responsible or partly responsible for an action identified as part of an initiative to develop a global strategy for the planet.

We are frustrated at the lack of progress this planet appears to be making towards providing the majority of its inhabitants with longer happier lives.
 
We look forward to your help in making the world a better place.  The specific action you have been tasked with supporting is:"""

    if db(db.app_message.msgtype == 'std').isempty():
        db.app_message.insert(msgtype='std', description='This is a general message without a specific action',
                              app_message_text=stdmsg)

    if db(db.app_message.msgtype == 'act').isempty():
        db.app_message.insert(msgtype='act', description='This is a message related to an  action',
                              app_message_text=actmsg)

    return locals()


@auth.requires_membership('manager')
def ajaxapprove():
    # This allows managers to approve pending registrations
    userid = request.args[0]
    upd = ''
    responsetext = 'User ' + str(userid) + ' has been approved'
    messagetxt = 'Your registration request has been approved'
    link = URL('default', 'index', scheme=True, host=True)
    footnote = 'You can now access the site at: ' + link
    if len(request.args) > 1:
        upd = 'denied'
        responsetext = 'User ' + str(userid) + ' has been denied access for now'
        messagetxt = 'Your registration request has been denied'
        footnote = 'A specific email will be sent to explain why or request more information'

    db(db.auth_user.id == userid).update(registration_key=upd)

    email = db(db.auth_user.id == userid).select(
        db.auth_user.email).first().email

    messagetxt = messagetxt + '\n' + footnote
    mail.send(to=email,
              subject='Networked Decision Making Registration Request',
              message=messagetxt)

    return responsetext

    
@auth.requires_membership('manager')    
def import_files():
    form = FORM(INPUT(_type='file', _name='data'), INPUT(_type='submit'))
    if form.process().accepted:
        db.import_from_csv_file(form.vars.data.file,unique=False)
        
    return locals()
    

@auth.requires_membership('manager')
def reset_event():
    # This will be driven from an event selection form -think we will allow any event to be reset
    # select events - thinking we will use SQLForm factory and select an event name - however
    # imported events may have duplicated name so will check for this and if duplicated then
    # will reset the latest event and amend the evt name
    
    query = (db.evt.id > 0)
    orderby = [~db.evt.createdate]
    rows = db(query).select(db.evt.evt_name, orderby=orderby)
    eventlist = [row.evt_name for row in rows]
    form = SQLFORM.factory(Field('event', requires = IS_IN_SET(eventlist, zero=T('choose one'))))
    if form.process().accepted:
        event_name = form.vars.event
        
        # Lets do event here for now as may want to list and confirm stuff
        eventquery = (db.evt.evt_name == event_name)
        orderby = [~db.evt.createdate]
        eventrows = db(query).select(db.evt.id, db.evt.evt_name, orderby=orderby)
        if len(eventrows) == 1:
            event = eventrows.first()
            eventid = event.id
        else:
            event = eventrows[-1]
            eventid = event.id
            event_name += '*reset*'
            query = (db.evt.id == eventid)
            db(query).update(evt_name = event_name)
                  
        query = (db.question.eventid == eventid)
        db(query).update(status = 'In Progress')
                
        # Thinking at present is this function will be for import only and so will not update 
        # userquestions
        
        response.flash = 'form accepted' + event_name + ' has been reset'
        
        # now select the questions for that event and for each row it would
        # get updated
        
    elif form.errors:
        response.flash = 'form has errors'
    return dict(form=form)


@auth.requires_membership('manager')
def score_complete_votes():
    # this will identify votes which are overdue based on being in progress
    # beyond due date and with resmethod of vote - probably shouldn't happen
    # but leave in for now for testing
    # There is currently no method to call this funcion from the menu but generally shouldn't be required

    votemethods = db(db.resolvemethod.method == 'Vote').select()
    votelist = [x.resolve_name for x in votemethods]

    query = (db.question.duedate > datetime.datetime.utcnow()) & (db.question.status == 'In Progress')
    quests = db(query).select()

    for x in quests:
        if x.resolvemethod in votelist:
            score_question(x.id)
    return True