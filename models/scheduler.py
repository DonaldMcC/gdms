from ndsfunctions import score_question
import datetime

def score_complete_votes():
    # this will identify votes which are overdue based on being in progress 
    # beyond due date and with resmethod of vote

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

from gluon.scheduler import Scheduler
scheduler = Scheduler(db)

#scheduler.queue_task(score_complete_votes, period=600)



            


