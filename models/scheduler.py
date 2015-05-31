from ndsfunctions import score_question
import datetime

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
            print('scoring'+ x.id) 
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
    if method == 'Vote':
        scheduler.queue_task(score_question,args=[id],start_time=duedate)
        print('Task scheduled for ')
        print(duedate)
        return True

    else:
        return False


# this will schedule scoring if a vote type question is created
# will add weekly and monthly in here once working
def schedule_emails():
    #scheduler.queue_task(email_activity, args=['daily','email'])
    a=1
    
    return True



# so now think we would also setup schedule emailing via a function in admin
# that calls the queue_taks and in general the tasks would run once and then resche
# dule themselves - seems fine - so basically as above
# start_time = request.noew + timed(seconds=30)
#

from gluon.scheduler import Scheduler
scheduler = Scheduler(db, heartbeat=15)


#scheduler.queue_task(schule_emails, args=['daily','email'])

#scheduler.queue_task(score_complete_votes, period=600)
