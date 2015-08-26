# - Coding UTF8 -
#
# Networked Decision Making
# Development Sites (source code): http://github.com/DonaldMcC/gdms
#
# Demo Sites (Google App Engine)
#   http://dmcc.pythonanywhere.com/gdmsprod/
#   http://dmcc.pythonanywhere.com/gdmsdemo/
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

from ndsfunctions import score_question, resulthtml, truncquest
import datetime

from gluon.scheduler import Scheduler
scheduler = Scheduler(db, heartbeat=15)


def score_complete_votes():
    # this will identify votes which are overdue based on being in progress 
    # beyond due date and with resmethod of vote 
    # superceded by below this is a generally poor approach to be deleted shortly

    votemethods = db(db.resolvemethod.method == 'Vote').select()
    votelist = [x.resolve_name for x in votemethods]

    query = (db.question.duedate > datetime.datetime.utcnow()) & (db.question.status == 'In Progress')
    quests = db(query).select()

    for x in quests:
        if x.resolvemethod in votelist:
            print('scoring' + x.id)
            score_question(x.id)
    if quests:
        print('processsed ' + str(len(quests)))
    else:
        print('zero items to process')
    return True


def activity(id=0, resend=False, period='weekly', format='html', source='default'):
    # Change of approach we are just going to call this with an id or a period - by default it will
    # attempt to find the next planned run and update

    db = current.db


    if id > 0:
        #get record
        parameters = db(db.email_runs.id == id).select().first()
        # if record status not equal to planned then log not sending to console and lets go with
        # only resending by id number
    else:
        parameters = db(db.email_runs.runperiod == period) & (db.email_runs.status == 'Planned').select().first()
        pass

    if parameters is None:
        return('No matching parameter record found')

    startdate = parameters.datefrom
    enddate = parameters.dateto
    #context = request.vars.context or 'Unspecified'

    filters = []
    # this can be Scope, Category, AnswerGroup and probably Event in due course

    crtquery = (db.question.createdate >= startdate) & (db.question.createdate <= enddate)
    resquery = (db.question.resolvedate >= startdate) & (db.question.resolvedate <= enddate)
    challquery = (db.question.challengedate >= startdate) & (db.question.challengedate <= enddate)

    orderstr = db.question.createdate
    resolvestr = db.question.resolvedate
    challstr = db.question.challengedate

    submitted = db(crtquery).select(orderby=orderstr)
    resolved = db(resquery).select(orderby=resolvestr)
    challenged = db(challquery).select(orderby=challstr)

    # below will need to change to select all users - but need to think about structure as may
    # be other things to mail and also need to get a format in place
    # remove excluded groups always

    print submitted

    sender = 'newglobalstrategy@gmail.com'
    subject = 'test activity'

    #for each user:
    to = 'newglobalstrategy@gmail.com'

    message = '<html><body><h1>Activity Report</h1>'
    # can do the row exclusions later


    message += "<h1>Items Submitted</h1>"
    if submitted:
        message += """<table><thead><tr>
                        <th width="5%">Type</th>
                        <th width="60%">Item Text</th>
                        <th width="13%">Scope</th>
                        <th width="12%">Category</th>
                        <th width="10%">Status</th>
                    </tr>
                </thead>
                    <tbody>"""
        for row in submitted:
            itemurl = URL('viewquest','index',args=[row.id],scheme='http', host='127.0.0.1:8081')
            itemtext = row.questiontext
            message += """<tr>
            <th><a href=%s>%s</a></th>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            </tr>""" % (itemurl, row.qtype, itemtext, row.scopetext, row.category, row.status)
        message += " </tbody></table>"
    else:
        message += "<p>No items submitted in the period.</p>"

    print(message)


    # then for each submitted, resolved and challenged
    # call some sort of function to create a table row

    # then send the message




    message += '</body></html>'
    send_email(to, sender, subject, message)

    print('run successful')
    return ('run successful')


# this will schedule scoring if a vote type question is created
# gets called from submit.py
def schedule_vote_counting(resolvemethod, id, duedate):    
    db = current.db
    resmethod = db(db.resolvemethod.resolve_name == resolvemethod).select().first()
    method = resmethod.method
    if method == 'VoteTime':
        # scheduler.queue_task(score_question, args=[id], start_time=duedate, period=600)
        scheduler.queue_task(score_question, start_time=duedate, pvars=dict(questid=id, endvote=True), period=600)
        # scheduler.queue_task(score_complete_votes, period=600)
        print('Task scheduled for ')
        print(duedate)
        return True

    else:
        return False


def send_email(to, sender, subject, message):
    # result =  mail.send(to=['somebody@example.com'], subject='hello', message='hi there')
    result = mail.send(to=to, sender=sender, subject=subject, message=message)
    return result

# this will run the scheduled email for a period and send out to 
# signed up recipients


def schedule_emails():
    # scheduler.queue_task(email_activity, args=['daily','email'])
    a = 1
    return True


# this is called from ndsfunctions if resolved
def email_resolved(questid):
    scheduler.queue_task(send_email_resolved, pvars=dict(questid=questid), period=600)
    return True


def send_email_resolved(questid):

    # For now this will find the resolved question and
    # check if owner wants to be notified if so email will be sent
    # else do nothing - may extend to sending to respondents in due course

    quest = db(db.question.id==questid).select().first()
    owner = db(db.auth_user.id == quest.auth_userid).select().first()

    if owner.emailresolved:
        subject = 'NDS - Item ' + str(questid) + ' has been resolved'
        message = resulthtml(quest.questiontext, quest.correctanstext())
        # message = quest.questiontext
        # message += 'User have resolved the correct answer is:'
        # message += quest.correctanstext()

        send_email(owner.email, mail.settings.sender, subject, message)

    return True

# so now think we would also setup schedule emailing via a function in admin
# that calls the queue_taks and in general the tasks would run once and then resche
# dule themselves - seems fine - so basically as above
# start_time = request.noew + timed(seconds=30)
