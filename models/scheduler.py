from ndsfunctions import score_question
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
            scorequestion(x.id)
    if quests:
        print('processsed ' + str(len(quests)))
    else:
        print('zero items to process')
    return True


# this will schedule scoring if a vote type question is created
# gets called from submit.py
def schedule_vote_counting(resolvemethod, id, duedate):    
    db = current.db
    resmethod = db(db.resolvemethod.resolve_name == resolvemethod).select().first()
    method = resmethod.method
    if method == 'VoteTime':
        # scheduler.queue_task(score_question, args=[id], start_time=duedate, period=600)
        scheduler.queue_task(score_question, start_time=duedate, pvars=dict(questid=id), period=600)
        # scheduler.queue_task(score_complete_votes, period=600)
        print('Task scheduled for ')
        print(duedate)
        return True

    else:
        return False


def send_email(to, sender, subject, reply_to, message):
    result =  mail.send(to=['somebody@example.com'],
          subject='hello',
          # If reply_to is omitted, then mail.settings.sender is used
          reply_to='us@example.com',
          message='hi there')
    return result

# this will run the scheduled email for a period and send out to 
# signed up recipients

def schedule_emails():
    # scheduler.queue_task(email_activity, args=['daily','email'])
    a = 1
    
    return True


def email_activity(period='daily'):

    # Find the previous one in the table if any if length less than max
    # Fix the period 
    # insert the record
    # find the users
    # if users extract the details
    # for each user filter on acces rights
    # send the email
    # update the record with how many sent and so on 

    return True


# this is called from ndsfunctions if resolved
def email_resolved(questid):
    scheduler.queue_task(send_email_resolved, pvars=dict(questid=questid), period=600)
    return True


def send_email_resolved(questid):

    # For now this will find the resolved question and
    # check if owner wants to be notified if so email will be sent
    # else do nothing - may extend to sending to respondents in due course

    return True

# so now think we would also setup schedule emailing via a function in admin
# that calls the queue_taks and in general the tasks would run once and then resche
# dule themselves - seems fine - so basically as above
# start_time = request.noew + timed(seconds=30)

