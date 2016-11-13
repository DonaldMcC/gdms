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

from ndsfunctions import score_question, resulthtml, truncquest, getrundates
import datetime
from ndspermt import get_exclude_groups

from gluon.scheduler import Scheduler
scheduler = Scheduler(db, heartbeat=15)


def activity(id=0, resend=False, period='Week', format='html', source='default'):
    # This will be triggered from runactivity function below which figures out if 
    # this needs to be run and on success rolls the run date forward for the next
    # period this just formats the message and formats for sending via email

    db = current.db

    if id > 0:
        rows = db(db.email_runs.id == id).select()
        # if record status not equal to planned then log not sending to console and lets go with
        # only resending by id number
    else:
        rows = db((db.email_runs.runperiod == period) & (db.email_runs.status == 'Planned')).select()

    if rows is None:
        print 'No matching parameter record found'
        return 'No matching parameter record found'

    parameters = rows.first()
    params = current.db(current.db.website_parameters.id > 0).select().first()
    
    if params:
        stripheader = params.website_url[7:]
    else:
        stripheader = 'website_url_not_setup'

    startdate = parameters.datefrom
    enddate = parameters.dateto

    crtquery = (db.question.createdate >= startdate) & (db.question.createdate <= enddate)
    resquery = (db.question.resolvedate >= startdate) & (db.question.resolvedate <= enddate)
    challquery = (db.question.challengedate >= startdate) & (db.question.challengedate <= enddate)

    orderstr = db.question.createdate
    resolvestr = db.question.resolvedate
    challstr = db.question.challengedate

    allsubmitted = db(crtquery).select(orderby=orderstr)
    resolved = db(resquery).select(orderby=resolvestr)
    challenged = db(challquery).select(orderby=challstr)

    sender = mail.settings.sender
    subject = 'NDS Activity Report'
    
    # get users for type of run
    if parameters.runperiod == 'Day':
        userquery = (db.auth_user.emaildaily == True)
        periodtext = 'Daily'
    elif parameters.runperiod == 'Week':
        userquery = (db.auth_user.emailweekly == True)
        periodtext = 'Weekly'
    elif parameters.runperiod == 'Month':
        periodtext = 'Monthly'
        userquery = (db.auth_user.emailmonthly == True)
    else:
        return('Invalid run period parameter - must be Day, Week or Month')

    users = db(userquery).select()
    message = ''
    for user in users:
        # print user.email
        to = user.email
        # will change above to create allsubmitteds and then do a filter

        exclude_groups = get_exclude_groups(user.id)
        if exclude_groups:
            submitted = allsubmitted.exclude(lambda r: r.answer_group not in exclude_groups)
        else:
            submitted = allsubmitted
    
        message = '<html><body><h1> ' + periodtext + ' Activity Report</h1>'

        # should be able to make personal as well
        # can do the row exclusions later

        # section below is basically taken from activtiy.i file in the view

        message += "<h1>Items Resolved</h1>"
        if resolved:
            message += """<table style="border: 1px solid DarkGreen;"><thead><tr>
                        <th width="5%">Type</th>
                        <th width="55%">Item Text</th>
                        <th width="15%">Answer</th>
                        <th width="8%"># Agree</th>
                        <th width="8%"># Disagree</th>
                        <th width="9%">Resolved</th>
                    </tr>
                </thead>
                    <tbody>"""
            for row in resolved:
                itemurl = URL('viewquest', 'index', args=[row.id], scheme='http', host=stripheader)
                itemtext = truncquest(row.questiontext)
                message += """<tr>
                <th><a href=%s>%s</a></th>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                </tr>""" % (itemurl, row.qtype, itemtext, row.correctanstext(), row.othercounts[3],
                            row.othercounts[3], row.resolvedate)
            message += " </tbody></table>"
        else:
            message += "<h3>No items resolved in the period.</h3>"

        message += "<h1>Items Submitted</h1>"
        if submitted:
            message += """<table style="border: 1px solid black;"><thead><tr>
                        <th width="5%">Type</th>
                        <th width="60%">Item Text</th>
                        <th width="13%">Scope</th>
                        <th width="12%">Category</th>
                        <th width="10%">Status</th>
                    </tr>
                </thead>
                    <tbody>"""
            for row in submitted:
                itemurl = URL('viewquest', 'index', args=[row.id], scheme='http', host=stripheader)
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
            message += "<h3>No items submitted in the period.</h3>"

        message += "<h1>Items Challenged</h1>"
        if challenged:
            message += """<table style="border: 1px solid DarkOrange;"><thead><tr>
                        <th width="5%">Level</th>
                        <th width="55%">Question</th>
                        <th width="15%">Answer</th>
                        <th width="8%"># Agree</th>
                        <th width="8%"># Disagree</th>
                        <th width="9%">Challenged</th>
                    </tr>
                </thead>
                    <tbody>"""
            for row in challenged:
                itemurl = URL('viewquest', 'index', args=[row.id], scheme='http', host=stripheader)
                itemtext = row.questiontext
                message += """<tr>

                <th><a href=%s>%s</a></th>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                </tr>""" % (itemurl, row.qtype, itemtext, row.correctanstext(), row.othercounts[3],
                            row.othercounts[3], row.resolvedate)
            message += " </tbody></table>"
        else:
            message += "<h3>No items challenged in the period.</h3>"
            
        message += '<p>This report covers the period from %s to %s.</p>' % (str(startdate), str(enddate))
        message += '</body></html>'

        if resolved or challenged or submitted:
            send_email(to, mail.settings.sender, subject, message)
        else:
            if debug:
                print subject, message
                send_email(to, mail.settings.sender, subject, message)
    print message

    return 'run successful'

    
# this schedules email when admin/datasteup has been completed
# gets called from admin.py datasetup
def schedule_email_runs(duedate=datetime.datetime.today()):
    scheduler.queue_task(runactivity, start_time=duedate, period=600, repeats=0)
    print('Email task scheduled for ')
    print(duedate)
    return True


def runactivity():
    # This would action all emails after the end date if run then
    # will refresh the dates for now but that may possibly also need to archive the record
    # will then call activity if necessary to actually run - otherwise do nothing
    result = 'starting run activity'

    currtime = datetime.datetime.today()
    to_run = db((db.email_runs.dateto <= currtime) & (db.email_runs.status == 'Planned')).select()
    if to_run:
        for row in to_run:
            runresult = activity(period=row.runperiod)
            print runresult
            newstartdate, newenddate = getrundates(period=row.runperiod, startdate=row.dateto)
            row.update_record(datefrom=newstartdate, dateto=newenddate)
            db.commit()
    else:
        print 'No scheduled emails this period'
    return result


# this will schedule scoring if a vote type question is created
# gets called from submit.py
def schedule_vote_counting(resolvemethod, id, duedate):    
    db = current.db
    resmethod = db(db.resolve.resolve_name == resolvemethod).select().first()
    method = resmethod.resolve_method
    if method == 'Vote':
        # scheduler.queue_task(score_question, args=[id], start_time=duedate, period=600)
        scheduler.queue_task(score_question, start_time=duedate, pvars=dict(questid=id, endvote=True), period=600)
        # scheduler.queue_task(score_complete_votes, period=600)
        print('Task scheduled for ')
        print(duedate)
        return True

    else:
        return False


def send_email(to, sender, subject, message):
    print to, sender, subject, message
    result = mail.send(to=to, sender=sender, subject=subject, message=message)
    return result


def email_resolved(questid):
    scheduler.queue_task(send_email_resolved, pvars=dict(questid=questid), period=600)
    return True


# this is called from ndsfunctions if resolved
def send_email_resolved(questid):
    # For now this will find the resolved question and
    # check if owner wants to be notified if so email will be sent
    # else do nothing - may extend to sending to respondents in due course

    quest = db(db.question.id == questid).select().first()
    owner = db(db.auth_user.id == quest.auth_userid).select().first()

    if owner.emailresolved:
        subject = 'Item resolved: ' + str(truncquest(quest.questiontext, 100, wrap=0, mark=False))
        message = resulthtml(quest.questiontext, quest.correctanstext(), questid)
        send_email(owner.email, mail.settings.sender, subject, message)

    return True
