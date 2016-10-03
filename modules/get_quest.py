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



if __name__ != '__main__':
    from gluon import *
    from ndspermt import get_exclude_groups, get_groups
    from ndsfunctions import getevent
    from geogfunctions import getbbox
    from graph_funcs import conv_for_iter, iter_dfs, get_trav_list
    from geogfunctions import getbbox

 
def update_session(quests, questtype): 
    for i, row in enumerate(quests):
        if i > 0:
            if current.session[questtype] :
                current.session[questtype].append(row.question.id)
            else:
                current.session[questtype] = [row.question.id]
    return
        

def getquestsql(questtype='quest', userid=None, excluded_categories=None, use_address=False):
    # This returns the next question for the user and builds a list of questions
    # to answer - extending support for local questions currently in progress and 
    # thinking is it should work like this
    # There is no obligation on users to provide there location or specify location restrictions
    # and if they don't then the existing process worked.  If they do then we will prioritise
    # local questions based on their location 

    current.session.exclude_groups = get_exclude_groups(userid)
    current.session.permitted_groups = get_groups(userid)
    questrow = 0
    debugsql = False
    debug = False

    if debug:
    categories:
            query &= ~(current.db.question.category.belongs(excluded_categories))

        if questtype != 'all':
            query &= (current.db.question.qtype == questtype)

        if current.auth.user.continent != 'Unspecified':  # some geographic restrictions
            # This is separate logic which applies when user has specified a continent - the general
            # thinking is that users cannot opt out of global questions but they may specify a continent
            # and optionally also a country and a subdivision in all cases we will be looking to    print (current.session.exclude_groups)

    orderstr = ''

    # TO DO if myconf.take('user.address'
    #This will be setup for local questions

    if use_address and current.auth.user.continent != 'Unspecified':
        minlat, minlong, maxlat, maxlong = getbbox(current.auth.user.coord, current.auth.user.localrange)

        for i in xrange(0, 3):
            if i == 0:
                query = (current.db.question.question_level == current.auth.user.userlevel) & (current.db.question.status == 'In Progress')
                orderstr = ~current.db.question.priority
            elif i == 1 and current.auth.user.userlevel >1:
                query = (current.db.question.question_level < current.auth.user.userlevel) & (current.db.question.status == 'In Progress')
                orderstr = ~current.db.question.question_level | ~current.db.question.priority
            elif i == 2:
                query = (current.db.question.question_level > current.auth.user.userlevel) & (current.db.question.status == 'In Progress')
                orderstr = current.db.question.question_level | ~current.db.question.priority
            elif i == 3:
                query = (current.db.question.status == 'In Progress')
                orderstr = ~current.db.question.priority

            query &= (current.db.userquestion.id == None)

            query &= (current.db.question.answer_group.belongs(current.session.permitted_groups))
            if excluded_categories:
                query &= ~(current.db.question.category.belongs(excluded_categories))

            if questtype != 'all':
                query &= (current.db.question.qtype == questtype)

            query &= (current.db.question.activescope == '5 Local')

            query &= ((current.db.question.question_lat > minlat) & (current.db.question.question_lat < maxlat) &
                 (current.db.question.question_long > minlong) & (current.db.question.question_long < maxlong))

            if debugsql:
                print(query)

            limitby = (0, 20)
            localquests = current.db(query).select(current.db.question.id, current.db.userquestion.id, current.db.question.category,
                                      left=current.db.userquestion.on((current.db.question.id==current.db.userquestion.questionid) &
                                                              (current.db.userquestion.auth_userid==userid) &
                                                              (current.db.userquestion.status == 'In Progress')), orderby=orderstr,
                                                               limitby=limitby)

            # TO DO might exclude  items based on radius here

            questrow = localquests.first()
            if questrow is not None:
                break
            #else:
            #    print 'no quest', i
            #    if debugsql:
            #        print(query)

        if questrow is not None:
            nextquestion = questrow.question.id
            update_session(localquests, questtype)
            return nextquestion # onlly local questions as these are being prioritised

    #This works for all questions with a scope that is not local or for users that don't have question set
    for i in xrange(0, 3):
        if i == 0:
            query = (current.db.question.question_level == current.auth.user.userlevel) & (current.db.question.status == 'In Progress')
            orderstr = ~current.db.question.priority
        elif i == 1 and current.auth.user.userlevel >1:
            query = (current.db.question.question_level < current.auth.user.userlevel) & (current.db.question.status == 'In Progress')
            orderstr = ~current.db.question.question_level | ~current.db.question.priority
        elif i == 2:
            query = (current.db.question.question_level > current.auth.user.userlevel) & (current.db.question.status == 'In Progress')
            orderstr = current.db.question.question_level | ~current.db.question.priority
        elif i == 3:
            query = (current.db.question.status == 'In Progress')
            orderstr = ~current.db.question.priority

        query &= (current.db.userquestion.id == None)

        query &= (current.db.question.answer_group.belongs(current.session.permitted_groups))
        if excluded_
            # run 4 queries the global and continental queries will always be the same but
            # the country and subdvision queries are conditional as country and subdivision
            # may be left unspecified in which case users should get all national quests for
            # their continent or all local questions for their country - we will attempt to

            if current.auth.user.country == 'Unspecified':
                query &=((current.db.question.activescope == '1 Global') |
                        ((current.db.question.continent == current.auth.user.continent) &
                        ((current.db.question.activescope == '2 Continental') |
                         (current.db.question.activescope == '3 National') | 
                         (current.db.question.activescope == '4 Provincial'))))
            else:  # country specified
                if current.auth.user.subdivision == 'Unspecified':
                    query &=((current.db.question.activescope == '1 Global') |
                            ((current.db.question.continent == current.session.auth.user.continent) &
                            ((current.db.question.activescope == '2 Continental'))) |
                            ((current.db.question.country == current.session.auth.user.country) &
                             ((current.db.question.activescope == '4 Provincial') |
                             (current.db.question.activescope == '3 National'))))
                else:
                    query &=((current.db.question.activescope == '1 Global') |
                            ((current.db.question.continent == current.auth.user.continent) &
                            (current.db.question.activescope == '2 Continental')) |
                            ((current.db.question.country == current.auth.user.country) &
                             (current.db.question.activescope == '3 National')) |
                            ((current.db.question.subdivision == current.auth.user.subdivision) &
                             (current.db.question.activescope == '4 Provincial')))

        if debugsql:
            print(query)

        limitby = (0, 20)
        quests = current.db(query).select(current.db.question.id, current.db.userquestion.id, current.db.question.category,
                                      left=current.db.userquestion.on((current.db.question.id==current.db.userquestion.questionid) &
                                                              (current.db.userquestion.auth_userid==userid) &
                                                              (current.db.userquestion.status == 'In Progress')), orderby=orderstr,
                                                               limitby=limitby)
        
        # Think we add local questions in here but maybe reasonable to allow prioritisation of local issues
        # and put at the top of the function with the global stuff being optional - no point getting if
        # too many local
        
        
        if debugsql:
            print current.db._lastsql

        questrow = quests.first()
        if questrow is not None:
            break

    # TO DO
    # could now merge quests and localquests but mandating local first for now if users specify location
    # so not doing this now
    
    if questrow is None:
        nextquestion = 0
    else:
        nextquestion = questrow.question.id
        update_session(quests, questtype)
        #for i, row in enumerate(quests):
        #    if i > 0:
        #        if current.session[questtype]:
        #            current.session[questtype].append(row.question.id)
        #        else:
        #            current.session[questtype] = [row.question.id]
    if debug:
        print (current.session[questtype])
    return nextquestion

def getquesteventsql(eventid, questtype='All', userid=None, excluded_categories=None):
    # so this will be sql based routine to navigate the event questions
    # result should be a list which will start at the top left based on the layout of the items
    # but it should then complete navigation of all links from that question and then restart
    # with next top left and repeat for the entire collection - the navigation needs to be 
    # across the full event but previously answered questions are skipped
    # there is no caring about issues, actions or questions these all flow but excluded questions
    # will break links

    current.session.exclude_groups = get_exclude_groups(userid)
    current.session.permitted_groups = get_groups(userid)
    questrow = 0
    debugsql = True
    debug = True

    orderstr = ''

    if eventid:
        ansquests = current.db((current.db.userquestion.auth_userid == current.session.auth.user) &
                       (current.db.userquestion.status == 'In Progress')).select(current.db.userquestion.questionid)
        if not current.session.answered:
            current.session.answered=[]
        for row in ansquests:
            current.session.answered.append(row.questionid)
            
        query = (current.db.question.eventid == eventid)
        orderstr = current.db.question.xpos

        query &= (current.db.question.answer_group.belongs(current.session.permitted_groups))

        if questtype != 'all':
            query &= (current.db.question.qtype == questtype)
        
        # Not sure whether sorting by x y is better or go the get event route
        quests, questlist=getevent(eventid, 'Open', 'Event')
        not_in_prog = [x.id for x in quests if x.status != 'In Progress']
        #print('nip', not_in_prog)
        
        if questlist:           
            #intlinks = getlinks(questlist)
            intquery = (current.db.questlink.targetid.belongs(questlist)) & (current.db.questlink.status == 'Active') & (
                    current.db.questlink.sourceid.belongs(questlist))
            intlinks = current.db(intquery).select()
            
            links = [x.sourceid for x in intlinks]
            linklist = [(x.sourceid, x.targetid, {'weight': 30}) for x in intlinks]
        
            G = conv_for_iter(questlist, linklist)
        
            sequencelist = list(iter_dfs(G, 0))

            questorderlist=get_trav_list(questlist, sequencelist)

            allquestsordered = questorderlist[1:] # remove event as first element which will be 0

            questwithanswered = [x for x in allquestsordered if x not in not_in_prog]

            if current.session.answered is None:
                current.session.answered = []
                ansquests = current.db((current.db.userquestion.auth_userid == current.session.auth.user) &
                       (current.db.userquestion.status == 'In Progress')).select(current.db.userquestion.questionid)
                for row in ansquests:
                    current.session.answered.append(row.questionid)
        
            questorderlist = [x for x in questwithanswered if x not in current.session.answered]

            if not questorderlist:
                nextquestion = 0
            else:
                nextquestion = questorderlist[0]
                update_session(quests, questtype)
            #for i, row in enumerate(questorderlist):
            #    if i > 0:
            #        current.session[questtype].append(row)
            #    else:
             #       current.session[questtype] = [row]
            if debug:
                print (current.session[questtype])
        else:
            nextquestion = 0
    else:
        nextquestion = 0
    return nextquestion

    
def getquestnonsql(questtype='quest', userid=None, excluded_categories=None):
    # This is called on non-sql datastores or if configured as non-sql - 
    # it is left for reference but not being maintained at present

    if current.session.answered is None:
        current.session.answered = []
        ansquests = current.db((current.db.userquestion.auth_userid == current.session.auth.user) &
                       (current.db.userquestion.status == 'In Progress')).select(current.db.userquestion.questionid)
        for row in ansquests:
            current.session.answered.append(row.questionid)
    current.session.exclude_groups = get_exclude_groups(userid)
    questrow = 0

    if debug:
        print (current.session.exclude_groups)

    orderstr = ''
    if current.session.auth.user.continent == 'Unspecified':  # ie no geographic restriction
        for i in xrange(0, 3):
            if i == 0:
                query = (current.db.question.question_level == current.session.auth.user.userlevel) & (current.db.question.status == 'In Progress')
                orderstr = ~current.db.question.priority
            elif i == 1:
                if current.auth.user.userlevel >1:
                    query = (current.db.question.question_level < current.session.auth.user.userlevel) & (current.db.question.status == 'In Progress')
                    orderstr = ~current.db.question.question_level | ~current.db.question.priority
            elif i == 2:
                query = (current.db.question.question_level > current.session.auth.user.userlevel) & (current.db.question.status == 'In Progress')
                orderstr = current.db.question.question_level | ~current.db.question.priority
            elif i == 3:
                query = (current.db.question.status == 'In Progress')
                orderstr = ~current.db.question.priority

            if questtype != 'all':
                query &= current.db.question.qtype == questtype

            quests = current.db(query).select(orderby=orderstr)
            questrow = quests.first()

            # exclude previously answered - this approach specifically taken rather than
            # an outer join so it can work on google app engine
            # then filter for unanswered and categories users dont want questions on
            alreadyans = quests.exclude(lambda row: row.id in current.session.answered)
            alreadyans = quests.exclude(lambda row: row.category in excluded_categories)
            alreadyans = quests.exclude(lambda row: row.answer_group in current.session.exclude_groups)

            questrow = quests.first()
            if questrow is not None:
                break
    else:
        # This is separate logic which applies when user has specified a continent - the general
        # thinking is that users cannot opt out of global questions but they may specify a continent
        # and optionally also a country and a subdivision in all cases we will be looking to
        # run 4 queries the global and continental queries will always be the same but
        # the country and subdvision queries are conditional as country and subdivision
        # may be left unspecified in which case users should get all national quests for
        # their continent or all local questions for their country - we will attempt to
        # keep the same logic surrounding levels shorlty

        for i in xrange(0, 3):
            if i == 0:
                query = (current.db.question.question_level == current.session.auth.user.userlevel) & (current.db.question.status == 'In Progress')
            elif i == 1:
                if current.auth.user.userlevel < 2:
                    continue
                else:
                    query = (current.db.question.question_level < current.session.auth.user.userlevel) & (current.db.question.status == 'In Progress')
            elif i == 2:
                query = (current.db.question.question_level > current.session.auth.user.userlevel) & (current.db.question.status == 'In Progress')
            elif i == 3:
                query = (current.db.question.status == 'In Progress')

            if questtype != 'all':
                query &= current.db.question.qtype == questtype
            qcont = query & (current.db.question.continent == current.session.auth.user.continent) & (
                current.db.question.activescope == '2 Continental')
            qglob = query & (current.db.question.activescope == '1 Global')

            if current.session.auth.user.country == 'Unspecified':
                qcount = query & (current.db.question.continent == current.session.auth.user.continent) & (
                    current.db.question.activescope == '3 National')
            else:
                qcount = query & (current.db.question.country == current.session.auth.user.country) & (current.db.question.activescope == '3 National')

            if current.session.auth.user.subdivision == 'Unspecified':
                qlocal = query & (current.db.question.country == current.session.auth.user.country) & (current.db.question.activescope == '4 Provincial')
            else:
                qlocal = query & (current.db.question.subdivision == current.session.auth.user.subdivision) & (
                    current.db.question.activescope == '4 Provincial')

            questglob = current.db(qglob).select(current.db.question.id, current.db.question.question_level, current.db.question.priority,
                                         current.db.question.category, current.db.question.answer_group)

            questcont = current.db(qcont).select(current.db.question.id, current.db.question.question_level, current.db.question.priority,
                                         current.db.question.category, current.db.question.answer_group)

            questcount = current.db(qcount).select(current.db.question.id, current.db.question.question_level, current.db.question.priority,
                                           current.db.question.category, current.db.question.answer_group)

            questlocal = current.db(qlocal).select(current.db.question.id, current.db.question.question_level, current.db.question.priority,
                                           current.db.question.category, current.db.question.answer_group)

            quests = (questglob | questcont | questcount | questlocal).sort(lambda r: r.priority, reverse=True)

            if current.session.answered:
                alreadyans = quests.exclude(lambda r: r.id in current.session.answered)
            if current.session.auth.user.exclude_categories:
                alreadyans = quests.exclude(lambda r: r.category in current.session.auth.user.exclude_categories)
            if current.session.exclude_groups:
                alreadyans = quests.exclude(lambda r: r.answer_group in current.session.exclude_groups)
            questrow = quests.first()

            if questrow is not None:
                break

    if questrow is None:
        nextquestion = 0
    else:
        nextquestion = questrow.id
        update_session(quests, questtype)
    #for i, row in enumerate(quests):
    #    if i > 0:
    #        if current.session[questtype]:
    #            current.session[questtype].append(row.id)
    #        else:
    #            current.session[questtype] = [row.id]

    return nextquestion