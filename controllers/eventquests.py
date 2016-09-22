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

# This adds some demonstration events and related questions
# looking to test a std system or have some desire to reperform the demo questions in a different environment
# so coding of this is awful think we need a list and then iterate through - but different questions have different
#  params and now got the challenge of setting up the links as well and needs to work on gae so a bit more than just
# looping through but probably can create a new list as we go of the questids inserted and then create the questlink
# table from that somehow need the list of links in a table and just map to the questids actually generated


@auth.requires_membership('manager')
def addndsquests():
    # Plan now is to have 3 programs to replace stdquests - while programatically poor it actually does seem
    # to need split up to process on gae without timeout or whatever issues so setting up 3 programs seems ok for now
    messagetext = 'NDS questions have been added'
    locationid = db(db.locn.location_name == 'Unspecified').select(db.locn.id).first().id
    projid = db(db.project.proj_name == 'Unspecified').select(db.project.id).first().id
    
    if db(db.evt.evt_name == "Net Decision Making Evolution").isempty():
        nds_id = db.evt.insert(evt_name="Net Decision Making Evolution", locationid=locationid, projid=projid,  evt_shared=False)
    else:
        messagetext = 'Event already setup no questions added'
        return dict(messagetext=messagetext)
    # eventmap = [[50, 50], [450, 100], [450, 350], [750, 600], [500, 600], [450, 900], [200, 650], [150, 350], [100,100]]

    ndsquests = [{'qtype': 'quest', 'questiontext': r'Is group decision making a problem?', 'answers': ["Yes", "No"], 'urgency': 4,
                  'importance': 7, 'category': 'Net Decision Making', 'eventid': nds_id, 'projid': projid, 'xpos': 50, 'ypos': 50 },
                 {'qtype': 'quest', 'questiontext': r'Would an online asynchronous decision making platform be beneficial?',
                  'answers': ["Yes", "No"], 'urgency': 4, 'importance': 7, 'category': 'Net Decision Making',
                  'eventid': nds_id, 'projid': projid, 'xpos': 450, 'ypos': 100},
                 {'qtype': 'action',
                  'questiontext': r'A prototype networked decision making system should be developed',  
                  'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 8, 'importance': 9,
                  'category': 'Net Decision Making',  'eventid': nds_id, 'projid': projid, 'xpos': 50, 'ypos': 50},
                 {'qtype': 'quest', 'questiontext': r'What is the best method to get feedback on Networked Decision Making?',
                   'answers': ["You need to draw users to the site and then review actions generated",
                    "Ask People directly", "Setup a surveyMonkey"], 'urgency': 4,
                  'importance': 7, 'category': 'Net Decision Making', 'eventid': nds_id, 'projid': projid, 'xpos': 50, 'ypos': 50},
                 {
                     'qtype': 'quest', 'questiontext': r'Should we develop social network integration features for networked decision making?',
                     'answers': ["Yes", "No"], 'urgency': 4, 'importance': 7, 'category': 'Net Decision Making',
                     'eventid': nds_id, 'projid': projid, 'xpos': 50, 'ypos': 50},
                 {'qtype': 'quest', 'questiontext': r'Which social networking platform should be developed first?',
                  'answers': ["Facebook", "Twitter", "Google+", "Other"], 'urgency': 4, 'importance': 7,
                  'category': 'Net Decision Making', 'eventid': nds_id, 'projid': projid, 'xpos': 50, 'ypos': 50},
                 {'qtype': 'quest', 'questiontext': r'Should we look to use advertising to fund the running costs of NDS?',
                  'answers': ["Yes", "No"], 'urgency': 4, 'importance': 7, 'category': 'Net Decision Making',
                  'eventid': nds_id, 'projid': projid, 'xpos': 50, 'ypos': 50},
                 {'qtype': 'action',
                  'questiontext': r'Google should develop a globally scaleable version of the network decision making system outlined here',
                    'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 7, 'importance': 7,
                  'category': 'Net Decision Making',  'eventid': nds_id, 'projid': projid, 'xpos': 50, 'ypos': 50},
                 {'qtype': 'issue',
                  'questiontext': r'NDS is not yet an accepted decision making mechanism',
                    'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 7, 'importance': 7,
                  'category': 'Net Decision Making',  'eventid': nds_id, 'projid': projid, 'xpos': 50, 'ypos': 50}]

    insertlist = []
    for x in ndsquests:
        qtext = x['questiontext']
        x['answercounts'] = [0]*(len(x['answers'])+1)
        q = 0
        if not request.env.web2py_runtime_gae:
            if db(db.question.questiontext == qtext).isempty():
                q = db.question.insert(**x)
        else:
            q = db.question.insert(**x)
        insertlist.append(q)
    # have assumed id of first action is 28 - this needs checked
    stdlinks = [[0, 1], [1, 2], [2, 3], [2, 4], [4, 5], [2, 6], [1, 7], [8,0]]

    # then if we have inserted those questions we would create related link

    for x in stdlinks:
        source_id = insertlist[x[0]]
        target_id = insertlist[x[1]]
        if source_id > 0 and target_id > 0:
            if db(db.questlink.sourceid == source_id and db.questlink.targetid == target_id).isempty():
                db.questlink.insert(sourceid=source_id, targetid=target_id, createcount=1, deletecount=0)

    # eventmap = [[50, 50], [450, 100], [450, 350], [750, 600], [500, 600], [450, 900], [200, 650], [150, 350], [100,100]]
    #for i, x in enumerate(eventmap):
    #    db.eventmap.insert(eventid=nds_id, questid=insertlist[i], xpos=eventmap[i][0], ypos=eventmap[i][1],
    #                       qtype=ndsquests[i]['qtype'], status='In Progress',
    #                       questiontext=ndsquests[i]['questiontext'], answers=ndsquests[i]['answers'],
    #                       urgency=ndsquests[i]['urgency'], importance=ndsquests[i]['importance'])

    return dict(messagetext=messagetext)


@auth.requires_membership('manager')
def addevtquests():
    # Plan now is to have 3 programs to replace stdquests - while programatically poor it actually does seem
    # to need split up to process on gae without timeout or whatever issues so setting up 3 programs seems ok for now

    messagetext = 'Strategy Event Quests Added'
    if db(db.evt.evt_name == "Global Strategy Review").isempty():
        locationid = db(db.locn.location_name == 'Unspecified').select(db.locn.id).first().id
        projid = db(db.project.proj_name == 'Unspecified').select(db.project.id).first().id
        gs_id = db.evt.insert(evt_name="Global Strategy Review", locationid=locationid, projid=projid, evt_shared=True)
    else:
        messagetext = 'Event already setup no questions added'
        return dict(messagetext=messagetext)

    # if db(db.event.event_name == "Net Decision Making Evolution").isempty():
    #    nds_event = db.event.insert(event_name="Net Decision Making Evolution", shared=False)

    # if db(db.event.event_name == "Global Healthcare Meeting").isempty():
    #   nds_event = db.event.insert(event_name="Global Healthcare Meeting", shared=True)

    eventmap = [[400, 0], [200, 450], [200, 200], [150, 750], [350, 750], [850, 550], [850, 300], [850, 0], [600, 700],
                [500, 300], [100,100]]

    gsquests = [{'qtype': 'quest', 'questiontext': r'Is the world under-achieving?', 'answers': ["Yes", "No"], 'urgency': 7,
                 'importance': 7, 'category': 'Organisation', 'eventid': gs_id, 'projid': projid, 'xpos': 450, 'ypos': 100},
                   {'qtype': 'quest', 'questiontext': r'Should we develop a global strategy as outlined at: http://www.ted.com/talks/jamie_drummond_how_to_set_goals_for_the_world.html ?',
                    'answers': ["Yes", "No"], 'urgency': 6, 'importance': 8, 'category': 'Strategy',
                    'eventid': gs_id, 'projid': projid, 'xpos': 450, 'ypos': 100},
                {'qtype': 'quest', 'questiontext': r'Are you aware of the global strategy?', 'answers': ["Yes", "No"], 'urgency': 7,
                 'importance': 7, 'category': 'Strategy', 'eventid': gs_id, 'projid': projid, 'xpos': 450, 'ypos': 100},
                {'qtype': 'quest', 'questiontext': r'Is it sensible to discuss consequences for failures to follow the global strategy?',
                 'answers': ["Yes", "No"], 'urgency': 7, 'importance': 7, 'category': 'Strategy',
                 'eventid': gs_id, 'projid': projid, 'xpos': 450, 'ypos': 100},
                {
                   'qtype': 'quest',  'questiontext': r'Is limiting access to future developments in healthcare a possible incentive to help people align their activities and behaviours',
                    'answers': ["Yes", "No"], 'urgency': 7, 'importance': 7, 'category': 'Strategy',
                    'eventid': gs_id, 'projid': projid, 'xpos': 450, 'ypos': 100},
                {
                   'qtype': 'quest',  'questiontext': r'Is The Zeitgeist Movement correct that humanity should move to a natural law, resource based economy?',
                    'answers': ["Yes", "No"], 'urgency': 7, 'importance': 7, 'category': 'Strategy',
                    'eventid': gs_id, 'projid': projid, 'xpos': 450, 'ypos': 100},
                {'qtype': 'quest', 'questiontext': r'What are the best solutions to work on right now?',
                 'answers': ["Prevention of HIV/Aids", "Networked Decision Making", "Malaria", "Malnutrition",
                             "Global Warming"], 'urgency': 8, 'importance': 8, 'category': 'Strategy',
                 'eventid': gs_id, 'projid': projid, 'xpos': 450, 'ypos': 100},

                {'qtype': 'quest', 'questiontext': r'What is the main problem with the world right now?',
                 'answers': ["There is no problem - everything is perfect",
                             "There simply isn't enough food in the world so some people have to starve",
                             "Many people don't care if other people are starving",
                             "Humans lack the skills to organise the planet",
                             "Humans derive pleasure from having more than other people",
                             "Lack of vision to see that creating alignment on objectives will get us all much better futures and longer and happier lives"],
                 'urgency': 7, 'importance': 8, 'category': 'Strategy', 'eventid': gs_id, 'projid': projid, 'xpos': 450, 'ypos': 100},
                {
                    'qtype': 'quest', 'questiontext': r'Is the United States a corruption as alleged at http://www.ted.com/talks/lawrence_lessig_we_the_people_and_the_republic_we_must_reclaim.html ?',
                    'answers': ["Yes", "No"], 'urgency': 7, 'importance': 7, 'category': 'Organisation',
                    'continent': 'North America (NA)', 'country': 'United States (NA)', 'activescope': '3 National',
                    'eventid': gs_id, 'projid': projid, 'xpos': 450, 'ypos': 100},
                {
                    'qtype': 'quest', 'questiontext': r'The distribution of wealth on the planet is radically different than that predicted by micro-economic theory.  The question therefore arises does acquisition of great wealth require exploitation of others?',
                      'answers': ["Yes", "No", "Usually"], 'urgency': 4, 'importance': 4,
                    'category': 'Strategy', 'eventid': gs_id, 'projid': projid, 'xpos': 450, 'ypos': 100},
                {
                    'qtype': 'issue', 'questiontext': r'This planet does not have an overall strategy to improve the lives of its inhabitants.',
                      'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 4, 'importance': 8,
                    'category': 'Strategy', 'eventid': gs_id, 'projid': projid, 'xpos': 450, 'ypos': 100}]

    insertlist = []
    for x in gsquests:
        qtext = x['questiontext']
        x['answercounts'] = [0]*(len(x['answers'])+1)
        q = 0
        if not request.env.web2py_runtime_gae:
            if db(db.question.questiontext == qtext).isempty():
                q = db.question.insert(**x)
        else:
            q = db.question.insert(**x)
        insertlist.append(q)

    # eventmap = [[400, 0], [200, 450], [200, 200], [150, 750], [350, 750], [850, 550], [850, 300], [850, 0], [600, 700],
    #            [500, 300], [100,100]]

    # for i, x in enumerate(eventmap):
    #    db.eventmap.insert(eventid=gs_id, questid=insertlist[i], xpos=eventmap[i][0], ypos=eventmap[i][1],
    #                       qtype=insertlist[i]['qtype'], status='In Progress',
    #                       questiontext=gsquests[i]['questiontext'], answers=gsquests[i]['answers'],
    #                       urgency=gsquests[i]['urgency'], importance=gsquests[i]['importance'])

    return dict(messagetext=messagetext)


@auth.requires_membership('manager')
def addhealthquests():
    # Plan now is to have 3 programs to replace stdquests - while programatically poor it actually does seem
    # to need split up to process on gae without timeout or whatever issues so setting up 3 programs seems ok for now
    messagetext = 'Health questions have been added'

    if db(db.evt.evt_name == "Healthcare Review").isempty():
        locationid = db(db.locn.location_name == 'Unspecified').select(db.locn.id).first().id
        projid = db(db.project.proj_name == 'Unspecified').select(db.project.id).first().id
        gs_id = db.evt.insert(evt_name="Healthcare Review", locationid=locationid, projid=projid, evt_shared=True)
    else:
        messagetext = 'Event already setup no questions added'
        return dict(messagetext=messagetext)

    eventmap = [[300, 50], [300, 350], [50, 500], [300, 600], [300, 850], [700, 450], [800, 750], [550, 750],
                [650, 200], [100,100]]

    stdquests = [
        {'qtype': 'quest', 'questiontext': r'Is aging a disease or is it just inevitable and we should accept it?',
         'answers': ["A disease", "Inevitable"], 'urgency': 4, 'importance': 7, 'category': 'Healthcare',
         'eventid': gs_id, 'projid': projid, 'xpos': 300, 'ypos': 50},
        {'qtype': 'quest', 'questiontext': r'Is it reasonable to try and promote biogerontology research?', 'answers': ["Yes", "No"],
         'urgency': 6, 'importance': 6, 'category': 'Healthcare', 'eventid': gs_id, 'projid': projid, 'xpos': 300, 'ypos': 350},
        {'qtype': 'quest', 'questiontext': r'Is it possible to live for more than 130 years?', 'answers': ["Yes", "No"], 'urgency': 4,
         'importance': 6, 'category': 'Healthcare', 'eventid': gs_id, 'projid': projid, 'xpos': 50, 'ypos': 500},
        {'qtype': 'quest', 'questiontext': r'Are we investing enough in aging research', 'answers': ["Yes", "No"], 'urgency': 4,
         'importance': 7, 'category': 'Healthcare', 'eventid': gs_id, 'projid': projid, 'xpos': 300, 'ypos': 600},
        {'qtype': 'action',
         'questiontext': r'Unless they have already done so, all global citizens with net assets in excess of US$100 million should invest 1% of their assets in biogerontology or related research and action. Eg The Gates Foundation activities and Ellison medical would both count so several leading individuals have done this already.',
           'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 8, 'importance': 8,
         'category': 'Healthcare',  'eventid': gs_id, 'projid': projid, 'xpos': 300, 'ypos': 850},
        {'qtype': 'action',
         'questiontext': r'The programme to deliver better housing as explained at http://www.ted.com/talks/paul_pholeros_how_to_reduce_poverty_fix_homes.html should be rolled out globally with associated crowdsourced measurement of progress.',
           'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 8, 'importance': 9,
         'category': 'Healthcare',  'eventid': gs_id, 'projid': projid, 'xpos': 700, 'ypos': 450},
        {'qtype': 'action',
         'questiontext': r'The top priority action from the 2012 Copenhagen Consensus (http://copenhagenconsensus.com) to use bundled micronutrient interventions to fight hunger and improve education should be actioned and funded by a $75bn cut to US defence spending',
           'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 8, 'importance': 9, 'category': 'Food',
          'eventid': gs_id, 'projid': projid, 'xpos': 800, 'ypos': 750},
        {
            'qtype': 'quest', 'questiontext': r'Is it reasonable to engage in debate on alternative eligibility criteria for new life extending healthcare',
            'answers': ["Yes", "No"], 'urgency': 4, 'importance': 7, 'category': 'Healthcare', 'eventid': gs_id, 'projid': projid, 'xpos': 550, 'ypos': 750},
        {
            'qtype': 'quest', 'questiontext': r'If behaviour as opposed to ability to pay became an accepted factor is this likely to change behaviour and improve the world?',
            'answers': ["Yes", "No"], 'urgency': 4, 'importance': 7, 'category': 'Healthcare', 'eventid': gs_id, 'projid': projid, 'xpos': 650, 'ypos': 200},
    {
            'qtype': 'issue', 'questiontext': r'Poor healthcare is reducing the quality of life for many people.',
            'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 8, 'importance': 8, 'category': 'Healthcare', 'eventid': gs_id, 'projid': projid, 'xpos': 100, 'ypos': 100}]


    insertlist = []
    for x in stdquests:
        qtext = x['questiontext']
        q = 0
        x['answercounts'] = [0]*(len(x['answers'])+1)
        if not request.env.web2py_runtime_gae:
            if db(db.question.questiontext == qtext).isempty():
                q = db.question.insert(**x)
        else:
            q = db.question.insert(**x)
        insertlist.append(q)
    # have assumed id of first action is 28 - this needs checked
    stdlinks = [[0, 1], [0, 2], [1, 3], [3, 4]]

    # then if we have inserted those questions we would create related link
    for x in stdlinks:
        source_id = insertlist[x[0]]
        target_id = insertlist[x[1]]
        if source_id > 0 and target_id > 0:
            if db(db.questlink.sourceid == source_id and db.questlink.targetid == target_id).isempty():
                db.questlink.insert(sourceid=source_id, targetid=target_id, createcount=1, deletecount=0)

    #eventmap = [[300, 50], [300, 350], [50, 500], [300, 600], [300, 850], [700, 450], [800, 750], [550, 750],
    #            [650, 200], [100,100]]

    #for i, x in enumerate(eventmap):
    #    db.eventmap.insert(eventid=gs_id, questid=insertlist[i], xpos=eventmap[i][0], ypos=eventmap[i][1],
    #                       qtype=stdquests[i]['qtype'], status='In Progress',
    #                       questiontext=stdquests[i]['questiontext'], answers=stdquests[i]['answers'],
    #                       urgency=stdquests[i]['urgency'], importance=stdquests[i]['importance'])

    return dict(messagetext=messagetext)


@auth.requires_membership('manager')
def addothquests():
    # Plan now is to have 4 programs to replace stdquests - while programatically poor it actually does seem
    # to need split up to process on gae without timeout or whatever issues so setting up 4 programs seems ok for now
    # this replaces std quests for other things we have eg philosophy etc no event on these and just paste
    # from stdquests

    evid = db(db.evt.evt_name == 'Unspecified').select(db.evt.id).first().id
    projid = db(db.project.proj_name == 'Unspecified').select(db.project.id).first().id

    messagetext = 'Other questions have been added'

    stdquests = [{'questiontext': r'Do we know if nothing is a stable state?',  
                  'answers': ["Yes", "No", "We don't know we just assume it is"], 'urgency': 3, 'importance': 6,
                  'category': 'Philosophy', 'eventid': evid, 'projid': projid},
                 {'questiontext': r'Is there sufficient education on when to compete and when to co-operate?',
                  'answers': ["Yes", "No"],
                  'urgency': 4, 'importance': 8, 'category': 'Strategy','eventid': evid, 'projid': projid},
                 {'questiontext': r'Did you choose where you were born?', 'answers': ["Yes", "No"], 'urgency': 4,
                  'importance': 4, 'category': 'Philosophy','eventid': evid, 'projid': projid},
                 {
                     'questiontext': r'Is it right that place of birth determines so much of your life and restricts so many people?',
                     'answers': ["Yes", "No"], 'urgency': 4, 'importance': 7, 'category': 'Philosophy','eventid': evid, 'projid': projid},
                 {'questiontext': r'Could we unite theists and atheists on a project to create heaven on earth?',
                  'answers': ["Yes", "No"], 'urgency': 7, 'importance': 7, 'category': 'Philosophy','eventid': evid, 'projid': projid},
                 {'questiontext': r'What is the optimum number of countries in the world?',
                  'answers': ["Just right", "Too many", "Too few", "One"], 'urgency': 5, 'importance': 8,
                  'category': 'Organisation', 'eventid': evid, 'projid': projid},
                 {'questiontext': r'What is the main problem with the world right now?',  
                  'answers': ["There is no problem - everything is perfect",
                              "There simply isn't enough food in the world so some people have to starve",
                              "Many people don't care if other people are starving",
                              "Humans lack the skills to organise the planet",
                              "Humans derive pleasure from having more than other people",
                              "Lack of vision to see that creating alignment on objectives will get us all much better futures and longer and happier lives"],
                  'urgency': 7, 'importance': 8, 'category': 'Strategy','eventid': evid, 'projid': projid},
                 {'questiontext': r'Does God Exist?', 'answers': ["Yes", "No"], 'urgency': 3, 'importance': 7,
                  'category': 'Philosophy','eventid': evid, 'projid': projid},
                 {'questiontext': r'Is God rational?', 'answers': ["Yes", "No"], 'urgency': 5, 'importance': 7,
                  'category': 'Philosophy','eventid': evid, 'projid': projid},
                 {'questiontext': r'Is it rational to believe in an irrational God?', 'answers': ["Yes", "No"],
                  'urgency': 6, 'importance': 7, 'category': 'Philosophy','eventid': evid, 'projid': projid},
                 {'questiontext': r'Do countries assist or hinder the operation of the world?',
                  'answers': ["Assist", "Hinder"], 'urgency': 6, 'importance': 7, 'category': 'Organisation', 'eventid': evid, 'projid': projid},
                 {'questiontext': r'Why are so many people unemployed?',  
                  'answers': ["The unemployed are all useless",
                              "Just a cost of human progress that many are left with lots of leisure but little income",
                              "Inability to co-operate, share and work together", "Many people are just lazy",
                              "Something else"], 'urgency': 8, 'importance': 7, 'category': 'Organisation','eventid': evid, 'projid': projid},
                 {
                     'questiontext': r'Did JFK speed-up or slow down progress in getting to the moon by explaining that was the intention in 1962  http://www.astrosociology.com/Library/PDF/JFK%201962%20Rice%20University%20Speech%20Transcript.pdf ?',
                     'answers': ["Speed Up", "Slow Down"], 'urgency': 7, 'importance': 7, 'category': 'Organisation','eventid': evid, 'projid': projid},
                 {
                     'questiontext': r"If stating we were going to the moon was important to getting there is there not a similarly strong case for saying we are going to extend human lifespans?",
                     'answers': ["Yes", "No"], 'urgency': 7, 'importance': 7, 'category': 'Organisation','eventid': evid, 'projid': projid},
                 {'questiontext': r'Should Scotland become an independent country?', 'answers': ["Yes", "No"],
                  'urgency': 4, 'importance': 7, 'category': 'Organisation', 'continent': 'Europe (EU)',
                  'country': 'United Kingdom (EU)', 'activescope': '3 National','eventid': evid, 'projid': projid},
                 {
                     'questiontext': r'Is the United States a corruption as alleged at http://www.ted.com/talks/lawrence_lessig_we_the_people_and_the_republic_we_must_reclaim.html ?',
                     'answers': ["Yes", "No"], 'urgency': 7, 'importance': 7, 'category': 'Organisation',
                     'continent': 'North America (NA)', 'country': 'United States (NA)', 'activescope': '3 National','eventid': evid, 'projid': projid},
                 {
                     'questiontext': r'The distribution of wealth on the planet is radically different than that predicted by micro-economic theory.  The question therefore arises does acquisition of great wealth require exploitation of others?',
                       'answers': ["Yes", "No", "Usually"], 'urgency': 4, 'importance': 4,
                     'category': 'Strategy','eventid': evid, 'projid': projid},
                 {'qtype': 'action',
                  'questiontext': r'Daylight saving time should operate all year in Europe to reduce accidents and CO2 emissions',
                    'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 8, 'importance': 9,
                  'category': 'Organisation',  'continent': 'Europe (EU)',
                  'activescope': '2 Continental','eventid': evid, 'projid': projid},
                 {'qtype': 'action', 'questiontext': r'The funding model for US politics must change',  
                  'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 8, 'importance': 9, 'category': 'Organisation',
                   'continent': 'North America (NA)', 'country': 'United States (NA)',
                  'activescope': '3 National','eventid': evid, 'projid': projid},
                 {'qtype': 'action',
                  'questiontext': r'All African health centres and schools should get internet access to improve access and trust in the global knowledge base, this should be provided by leading pharmaceutical and technology companies working together',
                    'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 5, 'importance': 9,
                  'category': 'Healthcare',
                  'continent': 'Africa (AF)', 'activescope': '2 Continental','eventid': evid, 'projid': projid},
                 {'qtype': 'action',
                  'questiontext': r'A national solution to the problem of misfuelling cars with petrol instead of diesel should be establised in the UK the costs of this problem are  estimated at around $120M per year and magnets, RFID readers on fuel pumps, better fuel caps or some other agreed approach should be able to permanently eliminate this waste for less than half that cost',
                    'answers': ['Approve', 'Disapprove', 'OK'], 'urgency': 5, 'importance': 6,
                  'category': 'Organisation',
                  'continent': 'Europe (EU)', 'country': 'United Kingdom (EU)', 'activescope': '3 National','eventid': evid, 'projid': projid}]

    insertlist = []
    for x in stdquests:
        qtext = x['questiontext']
        x['answercounts'] = [0]*(len(x['answers'])+1)
        q = 0
        if not request.env.web2py_runtime_gae:
            if db(db.question.questiontext == qtext).isempty():
                q = db.question.insert(**x)
        else:
            q = db.question.insert(**x)
            # time.sleep(1)
        insertlist.append(q)
    # have assumed id of first action is 28 - this needs checked
    stdlinks = [[8, 9], [11, 12]]

    for x in stdlinks:
        source_id = insertlist[x[0]]
        target_id = insertlist[x[1]]
        if source_id > 0 and target_id > 0:
            if db(db.questlink.sourceid == source_id and db.questlink.targetid == target_id).isempty():
                db.questlink.insert(sourceid=source_id, targetid=target_id, createcount=1, deletecount=0)

    return dict(messagetext=messagetext)