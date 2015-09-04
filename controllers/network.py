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
#
# This will be an initial contoller for displaying networks of questions
# current thinking is that layout will be managed server side and jointjs
# will handle the display and evnts side of things with networkx looking
# like the library for doing layouts with an underlying depenency on numpy
# General activities appear to be
# 1 get a list of nodes of some sort eg via search from events or locations
#   and possibly include 1 or 2 generations of links in either or both directions
# 2 get the links/edges between nodes
# 3 create a graph object and submit to networkx layout alogrithms and get a 
#   dictionary with positions of the nodes
# 4 in some way scale that to the proposed jointjs canvas looks like networkx is 
#   always square
# 5 Figure out how best to display the text and send results to jointjs
# 6 Collect new make link and delete link requests and decide whether to accept
#   or reject based on rules
# 7 Probably add rules to in some way pan and zoom through the network  - this 
#   may become computationally intense if large but initial stuff should be fine
#   getting more nodes via ajax looks doable but not sure about how the jointjs updates work
# created a networkforgaendb that supports belongs on datastore+ndb but will just revert to
# datastore for now and move on


from netx2py import getpositions
from ndsfunctions import creategraph, graphtojson, graphpositions, d3tojson
from jointjs2py import colourcode, textcolour, jsonportangle, jsonmetlink, getitemshape, getwraptext


def notindex2():
    # This is believed superceded by latest index
    # Thinking for now is that this will take zero one or two args for now
    # arg1 would be the number of generations to search and the default would be zero ie no
    # search for parents or children
    # arg 2 could be used for a single question id - however I think preference
    # is to start with some sort of session variable which would need to be populated by
    # any source which wants to call the mapping function - alternative of javascript array
    # seems clunky to pass across network - so will go with this for now
    # session.networklist will contain id, text status and correctanstext

    netdebug = False  # change to get extra details on the screen
    actlevels = 1
    basequest = 0
    resultstring = str(len(session.networklist))
    if len(request.args) > 0:
        numlevels = request.args[0]

    if len(request.args) > 1:
        basequest = request.args[1]

    if session.networklist is False:
        idlist = [basequest]
    else:
        idlist = session.networklist
    query = db.question.id.belongs(idlist)

    if idlist == 0:
        redirect(URL('no_questions'))

    quests = db(query).select()

    questlist = [x.id for x in quests]
    parentquery = (db.questlink.targetid.belongs(questlist)) & (db.questlink.status == 'Active')
    childquery = (db.questlink.sourceid.belongs(questlist)) & (db.questlink.status == 'Active')

    parentlist = questlist
    childlist = questlist

    links = None
    # just always have actlevels at 1 or more and see how that works
    # below just looks at parents and children - to get partners and siblings we could repeat the process
    # but that would extend to ancestors - so probably need to add as parameter to the query but conceptually this could
    # be repeated n number of times in due course

    # these may become parameters not sure
    # change back to true once working
    getsibs = False
    getpartners = False

    for x in range(actlevels):
        # ancestor proces
        if parentlist:
            # if not request.env.web2py_runtime_gae:
            parentlinks = db(parentquery).select()
            # else:
            #    parentlinks = None
            if links and parentlinks:
                links = links | parentlinks
            elif parentlinks:
                links = parentlinks
            if parentlinks:
                mylist = [y.sourceid for y in parentlinks]
                # query = db.question.id.belongs(mylist) & (db.questlink.status == 'Active')
                # above was accidental join
                query = db.question.id.belongs(mylist)
                parentquests = db(query).select()

                quests = quests | parentquests
                parentlist = [y.id for y in parentquests]
                if getsibs:
                    sibquery = db.questlink.sourceid.belongs(parentlist) & (db.questlink.status == 'Active')
                    siblinks = db(sibquery).select()
                    if siblinks:
                        links = links | siblinks
                        mylist = [y.targetid for y in siblinks]
                        query = db.question.id.belongs(mylist)
                        sibquests = db(query).select()
                        quests = quests | sibquests

                        # parentquery = db.questlink.targetid.belongs(parentlist)

                        # child process starts
        if childlist:
            # if not request.env.web2py_runtime_gae:
            childlinks = db(childquery).select()
            # else:
            #    childlinks = None
            if links and childlinks:
                links = links | childlinks
            elif childlinks:
                links = childlinks
            # childcount = db(childquery).count()
            # resultstring=str(childcount)
            if childlinks:
                mylist = [y.targetid for y in childlinks]
                query = db.question.id.belongs(mylist)
                childquests = db(query).select()
                quests = quests | childquests
                childlist = [y.id for y in childquests]
                if getpartners:
                    partquery = db.questlink.targetid.belongs(childlist)
                    partlinks = db(partquery).select()
                    if partlinks:
                        links = links | partlinks
                        mylist = [y.sourceid for y in partlinks]
                        query = db.question.id.belongs(mylist) & (db.questlink.status == 'Active')
                        partquests = db(query).select()
                        quests = quests | partquests
                        # childquery = db.questlink.sourceid.belongs(childlist)

    questlist = [y.id for y in quests]
    if links:
        linklist = [(y.sourceid, y.targetid) for y in links]
    else:
        linklist = []
    # ok so now got the question but need to get the list of links as well to draw the graph
    # same approach with a rows object
    nodepositions = getpositions(questlist, linklist)
    # thinking about doing a similar thing for parent child view - but not sure that's practical

    grwidth = 800
    grheight = 800

    # insert from viewquest to go through

    questmap = {}
    qlink = {}
    keys = '['
    z = 0
    for x in quests:
        z += 1
        if x['qtype'] == 'action':
            width = 200
            height = 140
            wraplength = 30
        else:
            width = 160
            height = 200
            wraplength = 25
        qtext = getwraptext(x.questiontext, x.correctanstext(), wraplength)
        rectcolour = colourcode(x.qtype, x.status, x.priority)
        colourtext = textcolour(x.qtype, x.status, x.priority)
        strobj = 'Nod' + str(x.id)
        questmap[strobj] = [nodepositions[x.id][0] * grwidth, nodepositions[x.id][1] * grheight, qtext, rectcolour, 12,

                            'lr', width, height, colourtext]
        keys += strobj
        keys += ','

    resultstring = str(z)
    # if we have siblings and partners and layout is directionless then may need to look at joining to the best port
    # or locating the ports at the best places on the shape - most questions will only have one or two connections
    # so two ports may well be enough we just need to figure out where the ports should be and then link to the
    # appropriate one think that means iterating through quests and links for each question but can set the
    # think we should move back to the idea of an in and out port and then position them possibly by rotation
    # on the document - work in progress

    if links:
        for x in links:
            strlink = 'Lnk' + str(x.id)
            strsource = 'Nod' + str(x.sourceid)
            strtarget = 'Nod' + str(x.targetid)
            if nodepositions[x.targetid][0] > nodepositions[x.sourceid][0]:
                sourceport = 'r'
                targetport = 'l'
            else:
                sourceport = 'l'
                targetport = 'r'
            if x.createcount - x.deletecount > 1:
                dasharray = False
                linethickness = min(3 + x.createcount, 7)
            else:
                dasharray = True
                linethickness = 3

            qlink[strlink] = [strsource, strtarget, sourceport, targetport, dasharray, linethickness]
            keys += strlink
            keys += ','

    keys = keys[:-1] + ']'

        # This should move to a function ideally as a pure function
    cellsjson = '['
    linkarray = '['

    for key, vals in questmap.iteritems():
        template = jsonportangle(key,vals[0],vals[1],vals[2],vals[3],vals[4],vals[6],vals[7],vals[5],vals[8])
        cellsjson += template + ','

    for key, vals in qlink.iteritems():
        template = jsonmetlink(key,vals[0],vals[1],vals[2],vals[3],vals[4])
        cellsjson += template + ','
        linkarray += '"' + key + '",'

    cellsjson = cellsjson[:-1]+']'
    linkarray = linkarray[:-1]+']'

    return dict(quests=quests, netdebug=netdebug, cellsjson=XML(cellsjson), linkarray=linkarray)
    # return dict(quests=quests, links=links, resultstring=resultstring, nodepositions=nodepositions, questmap=questmap,
    #            keys=keys, qlink=qlink, netdebug=netdebug, cellsjson=XML(cellsjson), linkarray=linkarray)


def interdemo():
    # This was copy of index2

    # and can probably be canned shortly but copied to graph to see if that can be got working and functions
    # now updated to graph format

    FIXWIDTH = 800
    FIXHEIGHT = 800

    redraw = request.vars.redraw

    netdebug = False  # change to get extra details on the screen
    actlevels = 1
    basequest = 0

    resultstring = str(len(session.networklist))
    numlevels = request.args(0, cast=int, default=1)
    basequest = request.args(1, cast=int, default=0)
    grwidth = request.args(2, cast=int, default=FIXWIDTH)
    grheight = request.args(3, cast=int, default=FIXHEIGHT)

    if session.networklist is False:
        idlist = [basequest]
    else:
        idlist = session.networklist
    query = db.question.id.belongs(idlist)

    if idlist == 0:
        redirect(URL('no_questions'))

    netgraph = creategraph(idlist, numlevels, intralinksonly=False)

    quests = netgraph['quests']
    links = netgraph['links']
    questlist = netgraph['questlist']
    linklist = netgraph['linklist']

    nodepositions = graphpositions(questlist, linklist)
    resultstring = netgraph['resultstring']

    print 'beflink'
    if links:
        for x in links:
            print x

    # oonvert graph to json representation for jointjs
    graphdict = graphtojson(quests, links, nodepositions, grwidth, grheight, False)
    # oonvert graph to json representation for d3
    d3dict = d3tojson(quests, links, nodepositions, grwidth, grheight, False)

    cellsjson = graphdict['cellsjson']
    keys = graphdict['keys']
    resultstring = graphdict['resultstring']

    d3jsondata =d3dict['cellsjson']

    d3jsondata = r'''
    {
  "nodes": [
    {
      "match": 1.0,
      "name": "Diamonds On The Soles Of Her Shoes",
      "artist": "Paul Simon",
      "id": "diamonds_on_the_soles_of_her_shoes_paul_simon",
      "playcount": 661020
    },
    {
      "match": 0.983114,
      "name": "Graceland",
      "artist": "Paul Simon",
      "id": "graceland_paul_simon",
      "playcount": 772823
    },
    {
      "match": 0.196092,
      "name": "Cecilia",
      "artist": "Simon & Garfunkel",
      "id": "cecilia_simon__garfunkel",
      "playcount": 1542594
    },
    {
      "match": 0.195602,
      "name": "Everywhere",
      "artist": "Fleetwood Mac",
      "id": "everywhere_fleetwood_mac",
      "playcount": 984941
    },
    {
      "match": 0.190388,
      "name": "The Boxer",
      "artist": "Simon & Garfunkel",
      "id": "the_boxer_simon__garfunkel",
      "playcount": 1889572
    },
    {
      "match": 0.183785,
      "name": "We Didn't Start The Fire",
      "artist": "Billy Joel",
      "id": "we_didnt_start_the_fire_billy_joel",
      "playcount": 1220636
    },
    {
      "match": 0.179382,
      "name": "Dancing In The Dark",
      "artist": "Bruce Springsteen",
      "id": "dancing_in_the_dark_bruce_springsteen",
      "playcount": 1534687
    },
    {
      "match": 0.179189,
      "name": "Uptown Girl",
      "artist": "Billy Joel",
      "id": "uptown_girl_billy_joel",
      "playcount": 1041806
    },
    {
      "match": 0.175134,
      "name": "Solsbury Hill",
      "artist": "Peter Gabriel",
      "id": "solsbury_hill_peter_gabriel",
      "playcount": 1146804
    },
    {
      "match": 0.173968,
      "name": "Little Lies",
      "artist": "Fleetwood Mac",
      "id": "little_lies_fleetwood_mac",
      "playcount": 1051253
    },
    {
      "match": 0.170235,
      "name": "The Boys Of Summer",
      "artist": "Don Henley",
      "id": "the_boys_of_summer_don_henley",
      "playcount": 924750
    },
    {
      "match": 1.0,
      "name": "The Boy In The Bubble",
      "artist": "Paul Simon",
      "id": "the_boy_in_the_bubble_paul_simon",
      "playcount": 521420
    },
    {
      "match": 0.129228,
      "name": "Bridge Over Troubled Water",
      "artist": "Simon & Garfunkel",
      "id": "bridge_over_troubled_water_simon__garfunkel",
      "playcount": 1603151
    },
    {
      "match": 1.0,
      "name": "El Condor Pasa (If I Could)",
      "artist": "Simon & Garfunkel",
      "id": "el_condor_pasa_if_i_could_simon__garfunkel",
      "playcount": 832548
    },
    {
      "match": 0.199443,
      "name": "Wild World",
      "artist": "Cat Stevens",
      "id": "wild_world_cat_stevens",
      "playcount": 1796394
    },
    {
      "match": 0.19272,
      "name": "You Can Call Me Al",
      "artist": "Paul Simon",
      "id": "you_can_call_me_al_paul_simon",
      "playcount": 1484544
    },
    {
      "match": 0.192459,
      "name": "50 Ways To Leave Your Lover",
      "artist": "Paul Simon",
      "id": "50_ways_to_leave_your_lover_paul_simon",
      "playcount": 515746
    },
    {
      "match": 0.179462,
      "name": "American Pie",
      "artist": "Don McLean",
      "id": "american_pie_don_mclean",
      "playcount": 1536335
    },
    {
      "match": 0.166708,
      "name": "Brown Eyed Girl",
      "artist": "Van Morrison",
      "id": "brown_eyed_girl_van_morrison",
      "playcount": 2056758
    },
    {
      "match": 0.160971,
      "name": "Tiny Dancer",
      "artist": "Elton John",
      "id": "tiny_dancer_elton_john",
      "playcount": 1877910
    },
    {
      "match": 0.15706,
      "name": "The Times They Are A-Changin'",
      "artist": "Bob Dylan",
      "id": "the_times_they_are_achangin_bob_dylan",
      "playcount": 2381122
    },
    {
      "match": 0.156131,
      "name": "Father And Son",
      "artist": "Cat Stevens",
      "id": "father_and_son_cat_stevens",
      "playcount": 1248643
    },
    {
      "match": 0.153536,
      "name": "Go Your Own Way",
      "artist": "Fleetwood Mac",
      "id": "go_your_own_way_fleetwood_mac",
      "playcount": 2187197
    },
    {
      "match": 0.151405,
      "name": "Blowin' in the Wind",
      "artist": "Bob Dylan",
      "id": "blowin_in_the_wind_bob_dylan",
      "playcount": 2473997
    },
    {
      "match": 0.900231,
      "name": "Seven Wonders",
      "artist": "Fleetwood Mac",
      "id": "seven_wonders_fleetwood_mac",
      "playcount": 341625
    },
    {
      "match": 0.205612,
      "name": "Edge of Seventeen",
      "artist": "Stevie Nicks",
      "id": "edge_of_seventeen_stevie_nicks",
      "playcount": 608369
    },
    {
      "match": 0.199102,
      "name": "Alone",
      "artist": "Heart",
      "id": "alone_heart",
      "playcount": 779908
    },
    {
      "match": 0.193764,
      "name": "I Want To Know What Love Is",
      "artist": "Foreigner",
      "id": "i_want_to_know_what_love_is_foreigner",
      "playcount": 1249625
    },
    {
      "match": 0.188842,
      "name": "We Built This City",
      "artist": "Starship",
      "id": "we_built_this_city_starship",
      "playcount": 660788
    },
    {
      "match": 0.181944,
      "name": "Nothing's Gonna Stop Us Now",
      "artist": "Starship",
      "id": "nothings_gonna_stop_us_now_starship",
      "playcount": 554636
    },
    {
      "match": 0.179991,
      "name": "Love Is A Battlefield",
      "artist": "Pat Benatar",
      "id": "love_is_a_battlefield_pat_benatar",
      "playcount": 894116
    },
    {
      "match": 0.17971,
      "name": "Keep On Loving You",
      "artist": "REO Speedwagon",
      "id": "keep_on_loving_you_reo_speedwagon",
      "playcount": 919767
    },
    {
      "match": 0.165724,
      "name": "Down Under",
      "artist": "Men at Work",
      "id": "down_under_men_at_work",
      "playcount": 1781012
    },
    {
      "match": 0.163831,
      "name": "In The Air Tonight",
      "artist": "Phil Collins",
      "id": "in_the_air_tonight_phil_collins",
      "playcount": 2089198
    },
    {
      "match": 0.160407,
      "name": "Invisible Touch",
      "artist": "Genesis",
      "id": "invisible_touch_genesis",
      "playcount": 719709
    },
    {
      "match": 0.216123,
      "name": "California Dreamin'",
      "artist": "The Mamas & The Papas",
      "id": "california_dreamin_the_mamas__the_papas",
      "playcount": 2547381
    },
    {
      "match": 0.203293,
      "name": "Like a Rolling Stone",
      "artist": "Bob Dylan",
      "id": "like_a_rolling_stone_bob_dylan",
      "playcount": 3906640
    },
    {
      "match": 0.20001,
      "name": "Mr. Tambourine Man",
      "artist": "The Byrds",
      "id": "mr_tambourine_man_the_byrds",
      "playcount": 995033
    },
    {
      "match": 0.191464,
      "name": "Good Vibrations",
      "artist": "The Beach Boys",
      "id": "good_vibrations_the_beach_boys",
      "playcount": 1947373
    },
    {
      "match": 0.190277,
      "name": "God Only Knows",
      "artist": "The Beach Boys",
      "id": "god_only_knows_the_beach_boys",
      "playcount": 2319988
    },
    {
      "match": 0.182734,
      "name": "For What It's Worth",
      "artist": "Buffalo Springfield",
      "id": "for_what_its_worth_buffalo_springfield",
      "playcount": 1912327
    },
    {
      "match": 0.179192,
      "name": "Heart Of Gold",
      "artist": "Neil Young",
      "id": "heart_of_gold_neil_young",
      "playcount": 2339041
    },
    {
      "match": 0.168376,
      "name": "Waterloo Sunset",
      "artist": "The Kinks",
      "id": "waterloo_sunset_the_kinks",
      "playcount": 1173497
    },
    {
      "match": 0.166218,
      "name": "Suzanne",
      "artist": "Leonard Cohen",
      "id": "suzanne_leonard_cohen",
      "playcount": 1432131
    },
    {
      "match": 0.163008,
      "name": "The Weight",
      "artist": "The Band",
      "id": "the_weight_the_band",
      "playcount": 1190720
    },
    {
      "match": 0.162638,
      "name": "Bad Moon Rising",
      "artist": "Creedence Clearwater Revival",
      "id": "bad_moon_rising_creedence_clearwater_revival",
      "playcount": 2533962
    },
    {
      "match": 1.0,
      "name": "The River Of Dreams",
      "artist": "Billy Joel",
      "id": "the_river_of_dreams_billy_joel",
      "playcount": 348368
    },
    {
      "match": 0.390405,
      "name": "Africa",
      "artist": "Toto",
      "id": "africa_toto",
      "playcount": 2528233
    },
    {
      "match": 0.363524,
      "name": "Jessie's Girl",
      "artist": "Rick Springfield",
      "id": "jessies_girl_rick_springfield",
      "playcount": 831375
    },
    {
      "match": 0.356831,
      "name": "Don't Stop Believin'",
      "artist": "Journey",
      "id": "dont_stop_believin_journey",
      "playcount": 4217289
    },
    {
      "match": 0.335493,
      "name": "Summer Of '69",
      "artist": "Bryan Adams",
      "id": "summer_of_69_bryan_adams",
      "playcount": 1704710
    },
    {
      "match": 0.331353,
      "name": "The Power Of Love",
      "artist": "Huey Lewis & The News",
      "id": "the_power_of_love_huey_lewis__the_news",
      "playcount": 739700
    },
    {
      "match": 0.300719,
      "name": "ROSANNA",
      "artist": "Toto",
      "id": "rosanna_toto",
      "playcount": 762116
    },
    {
      "match": 0.297477,
      "name": "Footloose",
      "artist": "Kenny Loggins",
      "id": "footloose_kenny_loggins",
      "playcount": 694839
    },
    {
      "match": 0.294044,
      "name": "Born In The U.S.A.",
      "artist": "Bruce Springsteen",
      "id": "born_in_the_usa_bruce_springsteen",
      "playcount": 1076590
    },
    {
      "match": 0.287821,
      "name": "Take Me Home Tonight",
      "artist": "Eddie Money",
      "id": "take_me_home_tonight_eddie_money",
      "playcount": 531471
    },
    {
      "match": 0.284582,
      "name": "Jump",
      "artist": "Van Halen",
      "id": "jump_van_halen",
      "playcount": 2051311
    },
    {
      "match": 1.0,
      "name": "Glory Days",
      "artist": "Bruce Springsteen",
      "id": "glory_days_bruce_springsteen",
      "playcount": 861323
    },
    {
      "match": 0.175427,
      "name": "Walk of Life",
      "artist": "Dire Straits",
      "id": "walk_of_life_dire_straits",
      "playcount": 2317528
    },
    {
      "match": 0.173322,
      "name": "Run To You",
      "artist": "Bryan Adams",
      "id": "run_to_you_bryan_adams",
      "playcount": 926655
    },
    {
      "match": 0.167739,
      "name": "Every Breath You Take",
      "artist": "The Police",
      "id": "every_breath_you_take_the_police",
      "playcount": 3177204
    },
    {
      "match": 0.151261,
      "name": "Money for Nothing",
      "artist": "Dire Straits",
      "id": "money_for_nothing_dire_straits",
      "playcount": 2674331
    },
    {
      "match": 0.145779,
      "name": "Free Fallin'",
      "artist": "Tom Petty",
      "id": "free_fallin_tom_petty",
      "playcount": 1036322
    },
    {
      "match": 0.1415,
      "name": "Every Little Thing She Does Is Magic",
      "artist": "The Police",
      "id": "every_little_thing_she_does_is_magic_the_police",
      "playcount": 1590002
    },
    {
      "match": 0.140492,
      "name": "Livin' On A Prayer",
      "artist": "Bon Jovi",
      "id": "livin_on_a_prayer_bon_jovi",
      "playcount": 3372830
    },
    {
      "match": 0.139546,
      "name": "I Still Haven't Found What I'm Looking For",
      "artist": "U2",
      "id": "i_still_havent_found_what_im_looking_for_u2",
      "playcount": 2744831
    },
    {
      "match": 0.139514,
      "name": "Pride (In The Name Of Love)",
      "artist": "U2",
      "id": "pride_in_the_name_of_love_u2",
      "playcount": 2056289
    },
    {
      "match": 0.13754,
      "name": "Start Me Up",
      "artist": "The Rolling Stones",
      "id": "start_me_up_the_rolling_stones",
      "playcount": 1669389
    },
    {
      "match": 1.0,
      "name": "Tell Her About It",
      "artist": "Billy Joel",
      "id": "tell_her_about_it_billy_joel",
      "playcount": 363383
    },
    {
      "match": 0.882343,
      "name": "The Longest Time",
      "artist": "Billy Joel",
      "id": "the_longest_time_billy_joel",
      "playcount": 645102
    },
    {
      "match": 0.267746,
      "name": "Manic Monday",
      "artist": "The Bangles",
      "id": "manic_monday_the_bangles",
      "playcount": 655160
    },
    {
      "match": 0.254366,
      "name": "You Can't Hurry Love",
      "artist": "Phil Collins",
      "id": "you_cant_hurry_love_phil_collins",
      "playcount": 689466
    },
    {
      "match": 0.247463,
      "name": "Who Can It Be Now?",
      "artist": "Men at Work",
      "id": "who_can_it_be_now_men_at_work",
      "playcount": 362836
    },
    {
      "match": 0.246162,
      "name": "Can't Fight This Feeling",
      "artist": "REO Speedwagon",
      "id": "cant_fight_this_feeling_reo_speedwagon",
      "playcount": 651138
    },
    {
      "match": 0.238669,
      "name": "I'm Still Standing",
      "artist": "Elton John",
      "id": "im_still_standing_elton_john",
      "playcount": 711736
    },
    {
      "match": 0.235425,
      "name": "I Guess That's Why They Call It The Blues",
      "artist": "Elton John",
      "id": "i_guess_thats_why_they_call_it_the_blues_elton_john",
      "playcount": 527872
    },
    {
      "match": 0.233698,
      "name": "Wake Me Up Before You Go-Go",
      "artist": "Wham!",
      "id": "wake_me_up_before_you_gogo_wham",
      "playcount": 676581
    },
    {
      "match": 0.226606,
      "name": "Any Way You Want It",
      "artist": "Journey",
      "id": "any_way_you_want_it_journey",
      "playcount": 1292330
    },
    {
      "match": 0.222163,
      "name": "Sweet Dreams (Are Made Of This)",
      "artist": "Eurythmics",
      "id": "sweet_dreams_are_made_of_this_eurythmics",
      "playcount": 1364473
    },
    {
      "match": 1.0,
      "name": "Red Rain",
      "artist": "Peter Gabriel",
      "id": "red_rain_peter_gabriel",
      "playcount": 457719
    },
    {
      "match": 0.939034,
      "name": "San Jacinto",
      "artist": "Peter Gabriel",
      "id": "san_jacinto_peter_gabriel",
      "playcount": 204179
    },
    {
      "match": 0.277371,
      "name": "Land Of Confusion",
      "artist": "Genesis",
      "id": "land_of_confusion_genesis",
      "playcount": 892956
    },
    {
      "match": 0.25747,
      "name": "Give A Little Bit",
      "artist": "Supertramp",
      "id": "give_a_little_bit_supertramp",
      "playcount": 622019
    },
    {
      "match": 0.244368,
      "name": "Owner Of A Lonely Heart",
      "artist": "Yes",
      "id": "owner_of_a_lonely_heart_yes",
      "playcount": 1247752
    },
    {
      "match": 0.226469,
      "name": "The Logical Song",
      "artist": "Supertramp",
      "id": "the_logical_song_supertramp",
      "playcount": 1566394
    },
    {
      "match": 0.217275,
      "name": "Message in a Bottle",
      "artist": "The Police",
      "id": "message_in_a_bottle_the_police",
      "playcount": 2432955
    },
    {
      "match": 0.202762,
      "name": "Sultans of Swing",
      "artist": "Dire Straits",
      "id": "sultans_of_swing_dire_straits",
      "playcount": 4089309
    },
    {
      "match": 0.19962,
      "name": "Kayleigh",
      "artist": "Marillion",
      "id": "kayleigh_marillion",
      "playcount": 846515
    },
    {
      "match": 0.197408,
      "name": "Heat of the Moment",
      "artist": "Asia",
      "id": "heat_of_the_moment_asia",
      "playcount": 929746
    },
    {
      "match": 0.192,
      "name": "Hold The Line",
      "artist": "Toto",
      "id": "hold_the_line_toto",
      "playcount": 1389928
    },
    {
      "match": 0.19066,
      "name": "Waiting For A Girl Like You",
      "artist": "Foreigner",
      "id": "waiting_for_a_girl_like_you_foreigner",
      "playcount": 645144
    },
    {
      "match": 0.187226,
      "name": "Don't Dream It's Over",
      "artist": "Crowded House",
      "id": "dont_dream_its_over_crowded_house",
      "playcount": 1142346
    },
    {
      "match": 0.176208,
      "name": "Drive",
      "artist": "The Cars",
      "id": "drive_the_cars",
      "playcount": 983164
    },
    {
      "match": 0.161265,
      "name": "Stand Back",
      "artist": "Stevie Nicks",
      "id": "stand_back_stevie_nicks",
      "playcount": 181603
    },
    {
      "match": 0.153712,
      "name": "Call Me",
      "artist": "Blondie",
      "id": "call_me_blondie",
      "playcount": 1532246
    },
    {
      "match": 0.153342,
      "name": "These Dreams",
      "artist": "Heart",
      "id": "these_dreams_heart",
      "playcount": 308248
    },
    {
      "match": 0.150528,
      "name": "Another Day In Paradise",
      "artist": "Phil Collins",
      "id": "another_day_in_paradise_phil_collins",
      "playcount": 1386894
    },
    {
      "match": 0.148892,
      "name": "Abracadabra",
      "artist": "Steve Miller Band",
      "id": "abracadabra_steve_miller_band",
      "playcount": 507682
    },
    {
      "match": 0.148815,
      "name": "Young Turks",
      "artist": "Rod Stewart",
      "id": "young_turks_rod_stewart",
      "playcount": 345502
    },
    {
      "match": 0.147889,
      "name": "Heart of Glass",
      "artist": "Blondie",
      "id": "heart_of_glass_blondie",
      "playcount": 2180131
    },
    {
      "match": 0.143878,
      "name": "Hungry Eyes",
      "artist": "Eric Carmen",
      "id": "hungry_eyes_eric_carmen",
      "playcount": 535640
    },
    {
      "match": 1.0,
      "name": "All She Wants To Do Is Dance",
      "artist": "Don Henley",
      "id": "all_she_wants_to_do_is_dance_don_henley",
      "playcount": 272117
    },
    {
      "match": 0.945483,
      "name": "The End Of The Innocence",
      "artist": "Don Henley",
      "id": "the_end_of_the_innocence_don_henley",
      "playcount": 260706
    },
    {
      "match": 0.663875,
      "name": "Oh Sherrie",
      "artist": "Steve Perry",
      "id": "oh_sherrie_steve_perry",
      "playcount": 199670
    },
    {
      "match": 0.568382,
      "name": "Broken Wings",
      "artist": "Mr. Mister",
      "id": "broken_wings_mr_mister",
      "playcount": 943840
    },
    {
      "match": 0.556606,
      "name": "Don't You (Forget About Me)",
      "artist": "Simple Minds",
      "id": "dont_you_forget_about_me_simple_minds",
      "playcount": 1080415
    },
    {
      "match": 0.556377,
      "name": "(I Just) Died In Your Arms",
      "artist": "Cutting Crew",
      "id": "i_just_died_in_your_arms_cutting_crew",
      "playcount": 693789
    },
    {
      "match": 0.556016,
      "name": "Your Love",
      "artist": "The Outfield",
      "id": "your_love_the_outfield",
      "playcount": 1067316
    },
    {
      "match": 0.496539,
      "name": "Faithfully",
      "artist": "Journey",
      "id": "faithfully_journey",
      "playcount": 939918
    },
    {
      "match": 0.469944,
      "name": "Kyrie",
      "artist": "Mr. Mister",
      "id": "kyrie_mr_mister",
      "playcount": 407294
    },
    {
      "match": 0.440955,
      "name": "Hurts So Good",
      "artist": "John Mellencamp",
      "id": "hurts_so_good_john_mellencamp",
      "playcount": 397742
    },
    {
      "match": 0.439593,
      "name": "Missing You",
      "artist": "John Waite",
      "id": "missing_you_john_waite",
      "playcount": 481722
    }
  ],
  "links": [
    {
      "source": "you_can_call_me_al_paul_simon",
      "target": "diamonds_on_the_soles_of_her_shoes_paul_simon"
    },
    {
      "source": "you_can_call_me_al_paul_simon",
      "target": "graceland_paul_simon"
    },
    {
      "source": "you_can_call_me_al_paul_simon",
      "target": "cecilia_simon__garfunkel"
    },
    {
      "source": "you_can_call_me_al_paul_simon",
      "target": "everywhere_fleetwood_mac"
    },
    {
      "source": "you_can_call_me_al_paul_simon",
      "target": "the_boxer_simon__garfunkel"
    },
    {
      "source": "you_can_call_me_al_paul_simon",
      "target": "we_didnt_start_the_fire_billy_joel"
    },
    {
      "source": "you_can_call_me_al_paul_simon",
      "target": "dancing_in_the_dark_bruce_springsteen"
    },
    {
      "source": "you_can_call_me_al_paul_simon",
      "target": "uptown_girl_billy_joel"
    },
    {
      "source": "you_can_call_me_al_paul_simon",
      "target": "solsbury_hill_peter_gabriel"
    },
    {
      "source": "you_can_call_me_al_paul_simon",
      "target": "little_lies_fleetwood_mac"
    },
    {
      "source": "you_can_call_me_al_paul_simon",
      "target": "the_boys_of_summer_don_henley"
    },
    {
      "source": "graceland_paul_simon",
      "target": "the_boy_in_the_bubble_paul_simon"
    },
    {
      "source": "graceland_paul_simon",
      "target": "bridge_over_troubled_water_simon__garfunkel"
    },
    {
      "source": "cecilia_simon__garfunkel",
      "target": "el_condor_pasa_if_i_could_simon__garfunkel"
    },
    {
      "source": "cecilia_simon__garfunkel",
      "target": "wild_world_cat_stevens"
    },
    {
      "source": "cecilia_simon__garfunkel",
      "target": "you_can_call_me_al_paul_simon"
    },
    {
      "source": "cecilia_simon__garfunkel",
      "target": "50_ways_to_leave_your_lover_paul_simon"
    },
    {
      "source": "cecilia_simon__garfunkel",
      "target": "american_pie_don_mclean"
    },
    {
      "source": "cecilia_simon__garfunkel",
      "target": "brown_eyed_girl_van_morrison"
    },
    {
      "source": "cecilia_simon__garfunkel",
      "target": "tiny_dancer_elton_john"
    },
    {
      "source": "cecilia_simon__garfunkel",
      "target": "the_times_they_are_achangin_bob_dylan"
    },
    {
      "source": "cecilia_simon__garfunkel",
      "target": "father_and_son_cat_stevens"
    },
    {
      "source": "cecilia_simon__garfunkel",
      "target": "go_your_own_way_fleetwood_mac"
    },
    {
      "source": "cecilia_simon__garfunkel",
      "target": "blowin_in_the_wind_bob_dylan"
    },
    {
      "source": "everywhere_fleetwood_mac",
      "target": "seven_wonders_fleetwood_mac"
    },
    {
      "source": "everywhere_fleetwood_mac",
      "target": "edge_of_seventeen_stevie_nicks"
    },
    {
      "source": "everywhere_fleetwood_mac",
      "target": "alone_heart"
    },
    {
      "source": "everywhere_fleetwood_mac",
      "target": "i_want_to_know_what_love_is_foreigner"
    },
    {
      "source": "everywhere_fleetwood_mac",
      "target": "we_built_this_city_starship"
    },
    {
      "source": "everywhere_fleetwood_mac",
      "target": "nothings_gonna_stop_us_now_starship"
    },
    {
      "source": "everywhere_fleetwood_mac",
      "target": "love_is_a_battlefield_pat_benatar"
    },
    {
      "source": "everywhere_fleetwood_mac",
      "target": "keep_on_loving_you_reo_speedwagon"
    },
    {
      "source": "everywhere_fleetwood_mac",
      "target": "down_under_men_at_work"
    },
    {
      "source": "everywhere_fleetwood_mac",
      "target": "in_the_air_tonight_phil_collins"
    },
    {
      "source": "everywhere_fleetwood_mac",
      "target": "invisible_touch_genesis"
    },
    {
      "source": "the_boxer_simon__garfunkel",
      "target": "california_dreamin_the_mamas__the_papas"
    },
    {
      "source": "the_boxer_simon__garfunkel",
      "target": "like_a_rolling_stone_bob_dylan"
    },
    {
      "source": "the_boxer_simon__garfunkel",
      "target": "mr_tambourine_man_the_byrds"
    },
    {
      "source": "the_boxer_simon__garfunkel",
      "target": "good_vibrations_the_beach_boys"
    },
    {
      "source": "the_boxer_simon__garfunkel",
      "target": "god_only_knows_the_beach_boys"
    },
    {
      "source": "the_boxer_simon__garfunkel",
      "target": "for_what_its_worth_buffalo_springfield"
    },
    {
      "source": "the_boxer_simon__garfunkel",
      "target": "heart_of_gold_neil_young"
    },
    {
      "source": "the_boxer_simon__garfunkel",
      "target": "waterloo_sunset_the_kinks"
    },
    {
      "source": "the_boxer_simon__garfunkel",
      "target": "suzanne_leonard_cohen"
    },
    {
      "source": "the_boxer_simon__garfunkel",
      "target": "the_weight_the_band"
    },
    {
      "source": "the_boxer_simon__garfunkel",
      "target": "bad_moon_rising_creedence_clearwater_revival"
    },
    {
      "source": "we_didnt_start_the_fire_billy_joel",
      "target": "the_river_of_dreams_billy_joel"
    },
    {
      "source": "we_didnt_start_the_fire_billy_joel",
      "target": "africa_toto"
    },
    {
      "source": "we_didnt_start_the_fire_billy_joel",
      "target": "jessies_girl_rick_springfield"
    },
    {
      "source": "we_didnt_start_the_fire_billy_joel",
      "target": "dont_stop_believin_journey"
    },
    {
      "source": "we_didnt_start_the_fire_billy_joel",
      "target": "summer_of_69_bryan_adams"
    },
    {
      "source": "we_didnt_start_the_fire_billy_joel",
      "target": "the_power_of_love_huey_lewis__the_news"
    },
    {
      "source": "we_didnt_start_the_fire_billy_joel",
      "target": "rosanna_toto"
    },
    {
      "source": "we_didnt_start_the_fire_billy_joel",
      "target": "footloose_kenny_loggins"
    },
    {
      "source": "we_didnt_start_the_fire_billy_joel",
      "target": "born_in_the_usa_bruce_springsteen"
    },
    {
      "source": "we_didnt_start_the_fire_billy_joel",
      "target": "take_me_home_tonight_eddie_money"
    },
    {
      "source": "we_didnt_start_the_fire_billy_joel",
      "target": "jump_van_halen"
    },
    {
      "source": "dancing_in_the_dark_bruce_springsteen",
      "target": "glory_days_bruce_springsteen"
    },
    {
      "source": "dancing_in_the_dark_bruce_springsteen",
      "target": "walk_of_life_dire_straits"
    },
    {
      "source": "dancing_in_the_dark_bruce_springsteen",
      "target": "run_to_you_bryan_adams"
    },
    {
      "source": "dancing_in_the_dark_bruce_springsteen",
      "target": "every_breath_you_take_the_police"
    },
    {
      "source": "dancing_in_the_dark_bruce_springsteen",
      "target": "money_for_nothing_dire_straits"
    },
    {
      "source": "dancing_in_the_dark_bruce_springsteen",
      "target": "free_fallin_tom_petty"
    },
    {
      "source": "dancing_in_the_dark_bruce_springsteen",
      "target": "every_little_thing_she_does_is_magic_the_police"
    },
    {
      "source": "dancing_in_the_dark_bruce_springsteen",
      "target": "livin_on_a_prayer_bon_jovi"
    },
    {
      "source": "dancing_in_the_dark_bruce_springsteen",
      "target": "i_still_havent_found_what_im_looking_for_u2"
    },
    {
      "source": "dancing_in_the_dark_bruce_springsteen",
      "target": "pride_in_the_name_of_love_u2"
    },
    {
      "source": "dancing_in_the_dark_bruce_springsteen",
      "target": "start_me_up_the_rolling_stones"
    },
    {
      "source": "uptown_girl_billy_joel",
      "target": "tell_her_about_it_billy_joel"
    },
    {
      "source": "uptown_girl_billy_joel",
      "target": "the_longest_time_billy_joel"
    },
    {
      "source": "uptown_girl_billy_joel",
      "target": "manic_monday_the_bangles"
    },
    {
      "source": "uptown_girl_billy_joel",
      "target": "you_cant_hurry_love_phil_collins"
    },
    {
      "source": "uptown_girl_billy_joel",
      "target": "who_can_it_be_now_men_at_work"
    },
    {
      "source": "uptown_girl_billy_joel",
      "target": "cant_fight_this_feeling_reo_speedwagon"
    },
    {
      "source": "uptown_girl_billy_joel",
      "target": "im_still_standing_elton_john"
    },
    {
      "source": "uptown_girl_billy_joel",
      "target": "i_guess_thats_why_they_call_it_the_blues_elton_john"
    },
    {
      "source": "uptown_girl_billy_joel",
      "target": "wake_me_up_before_you_gogo_wham"
    },
    {
      "source": "uptown_girl_billy_joel",
      "target": "any_way_you_want_it_journey"
    },
    {
      "source": "uptown_girl_billy_joel",
      "target": "sweet_dreams_are_made_of_this_eurythmics"
    },
    {
      "source": "solsbury_hill_peter_gabriel",
      "target": "red_rain_peter_gabriel"
    },
    {
      "source": "solsbury_hill_peter_gabriel",
      "target": "san_jacinto_peter_gabriel"
    },
    {
      "source": "solsbury_hill_peter_gabriel",
      "target": "land_of_confusion_genesis"
    },
    {
      "source": "solsbury_hill_peter_gabriel",
      "target": "give_a_little_bit_supertramp"
    },
    {
      "source": "solsbury_hill_peter_gabriel",
      "target": "owner_of_a_lonely_heart_yes"
    },
    {
      "source": "solsbury_hill_peter_gabriel",
      "target": "the_logical_song_supertramp"
    },
    {
      "source": "solsbury_hill_peter_gabriel",
      "target": "message_in_a_bottle_the_police"
    },
    {
      "source": "solsbury_hill_peter_gabriel",
      "target": "sultans_of_swing_dire_straits"
    },
    {
      "source": "solsbury_hill_peter_gabriel",
      "target": "kayleigh_marillion"
    },
    {
      "source": "solsbury_hill_peter_gabriel",
      "target": "heat_of_the_moment_asia"
    },
    {
      "source": "solsbury_hill_peter_gabriel",
      "target": "hold_the_line_toto"
    },
    {
      "source": "little_lies_fleetwood_mac",
      "target": "waiting_for_a_girl_like_you_foreigner"
    },
    {
      "source": "little_lies_fleetwood_mac",
      "target": "dont_dream_its_over_crowded_house"
    },
    {
      "source": "little_lies_fleetwood_mac",
      "target": "drive_the_cars"
    },
    {
      "source": "little_lies_fleetwood_mac",
      "target": "stand_back_stevie_nicks"
    },
    {
      "source": "little_lies_fleetwood_mac",
      "target": "call_me_blondie"
    },
    {
      "source": "little_lies_fleetwood_mac",
      "target": "these_dreams_heart"
    },
    {
      "source": "little_lies_fleetwood_mac",
      "target": "another_day_in_paradise_phil_collins"
    },
    {
      "source": "little_lies_fleetwood_mac",
      "target": "abracadabra_steve_miller_band"
    },
    {
      "source": "little_lies_fleetwood_mac",
      "target": "young_turks_rod_stewart"
    },
    {
      "source": "little_lies_fleetwood_mac",
      "target": "heart_of_glass_blondie"
    },
    {
      "source": "little_lies_fleetwood_mac",
      "target": "hungry_eyes_eric_carmen"
    },
    {
      "source": "the_boys_of_summer_don_henley",
      "target": "all_she_wants_to_do_is_dance_don_henley"
    },
    {
      "source": "the_boys_of_summer_don_henley",
      "target": "the_end_of_the_innocence_don_henley"
    },
    {
      "source": "the_boys_of_summer_don_henley",
      "target": "oh_sherrie_steve_perry"
    },
    {
      "source": "the_boys_of_summer_don_henley",
      "target": "broken_wings_mr_mister"
    },
    {
      "source": "the_boys_of_summer_don_henley",
      "target": "dont_you_forget_about_me_simple_minds"
    },
    {
      "source": "the_boys_of_summer_don_henley",
      "target": "i_just_died_in_your_arms_cutting_crew"
    },
    {
      "source": "the_boys_of_summer_don_henley",
      "target": "your_love_the_outfield"
    },
    {
      "source": "the_boys_of_summer_don_henley",
      "target": "faithfully_journey"
    },
    {
      "source": "the_boys_of_summer_don_henley",
      "target": "kyrie_mr_mister"
    },
    {
      "source": "the_boys_of_summer_don_henley",
      "target": "hurts_so_good_john_mellencamp"
    },
    {
      "source": "the_boys_of_summer_don_henley",
      "target": "missing_you_john_waite"
    }
  ]
    }'''

    return dict(cellsjson=XML(cellsjson), links=links, resultstring=resultstring,
                quests=quests,  keys=keys, netdebug=netdebug, d3jsondata=d3jsondata)

def index2():
    # Thinking for now is that this will take zero one or two args for now
    # arg1 would be the number of generations to search and the default would be zero ie no
    # search for parents or children
    # arg 2 could be used for a single question id - however I think preference
    # is to start with some sort of session variable which would need to be populated by
    # any source which wants to call the mapping function - alternative of javascript array
    # seems clunky to pass across network - so will go with this for now
    # session.networklist will contain id, text status and correctanstext

    FIXWIDTH = 800
    FIXHEIGHT = 800

    redraw = request.vars.redraw

    netdebug = False  # change to get extra details on the screen
    actlevels = 1
    basequest = 0

    resultstring = str(len(session.networklist))
    numlevels = request.args(0, cast=int, default=1)
    basequest = request.args(1, cast=int, default=0)
    grwidth = request.args(2, cast=int, default=FIXWIDTH)
    grheight = request.args(3, cast=int, default=FIXHEIGHT)

    if session.networklist is False:
        idlist = [basequest]
    else:
        idlist = session.networklist
    query = db.question.id.belongs(idlist)

    if idlist == 0:
        redirect(URL('no_questions'))

    netgraph = creategraph(idlist, numlevels, intralinksonly=False)

    quests = netgraph['quests']
    links = netgraph['links']
    questlist = netgraph['questlist']
    linklist = netgraph['linklist']

    nodepositions = graphpositions(questlist, linklist)
    resultstring = netgraph['resultstring']

    print 'beflink'
    for x in links:
        print x

    # oonvert graph to json representation for jointjs
    graphdict = graphtojson(quests, links, nodepositions, grwidth, grheight, False)

    cellsjson = graphdict['cellsjson']
    keys = graphdict['keys']
    resultstring = graphdict['resultstring']

    return dict(cellsjson=XML(cellsjson), links=links, resultstring=resultstring,
                quests=quests,  keys=keys, netdebug=netdebug)


def linkrequest():
    # this is called when a link is requested from the qmap or other function
    # at present we are keeping limited audit trail on link requests - only last updater
    # and last action and the basic rule is that the last action cannot be repeated
    # we don't currently know if this function will also be used for deletions but
    # currently it won't as there is no action in the args only the sourc and target links
    # so action for now is to estblish if the link already exists and if not create it
    # if it exists the number of requests increases and last user and action are updated.

    # now proposing to have an action as arg 3 which could be delete or agree
    # with link - this should be OK
    # and wil style the links a bit based on this too

    if len(request.args) < 2:
        # sourceid = request.args[0]
        # targetid = request.args[1]
        result = 'not enough args dont call me please'

    else:
        sourceid = request.args[0]
        targetid = request.args[1]
        if auth.user is None:
            result = 'You must be logged in to create links'
        else:
            linkaction = 'create'
            if len(request.args) > 2:
                linkaction = request.args[2]

            parquestid = sourceid[3:]
            chiquestid = targetid[3:]

            result = 'Ajax submitted ' + sourceid + ' with ' + targetid + ':' + parquestid + ' ' + chiquestid

            query = (db.questlink.sourceid == parquestid) & (db.questlink.targetid == chiquestid)

            linkrows = db(query).select().first()

            if linkrows is None:
                db.questlink.insert(sourceid=parquestid, targetid=chiquestid)
                # Now also need to add 1 to the numagreement or disagreement figure
                # It shouldn't be possible to challenge unless resolved
                result += ' Link Created'
            else:
                # link exists 
                if linkaction == 'create':
                    if linkrows.createdby == auth.user_id:
                        result = result + ' ' + 'You updated last no change made'
                    else:
                        agrcount = linkrows.createcount + 1
                        linkrows.update_record(createcount=agrcount)
                elif linkaction == 'delete':
                    if linkrows.createdby == auth.user_id and linkrows.createcount == 1:
                        db(db.questlink.id == linkrows.id).delete()
                        result = 'Row deleted'
                    else:
                        if linkrows.lastdeleter == auth.user_id:
                            result = result + ' ' + 'You deleted last no change made'
                        else:
                            delcount = linkrows.deletecount + 1
                            if delcount >= linkrows.createcount:
                                status = 'Deleted'
                            else:
                                status = 'Active'
                            linkrows.update_record(lastaction='delete', deletecount=delcount, lastdeleter=auth.user_id,
                                                   status=status)
                            result = 'Deletion count updated'

    return result


def graph():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")

    FIXWIDTH = 800
    FIXHEIGHT = 800

    redraw = request.vars.redraw

    netdebug = False  # change to get extra details on the screen
    actlevels = 1
    basequest = 0

    resultstring = str(len(session.networklist))
    numlevels = request.args(0, cast=int, default=1)
    basequest = request.args(1, cast=int, default=0)
    grwidth = request.args(2, cast=int, default=FIXWIDTH)
    grheight = request.args(3, cast=int, default=FIXHEIGHT)

    if session.networklist is False:
        idlist = [basequest]
    else:
        idlist = session.networklist
    query = db.question.id.belongs(idlist)

    if idlist == 0:
        redirect(URL('no_questions'))

    netgraph = creategraph(idlist, numlevels, intralinksonly=False)

    quests = netgraph['quests']
    links = netgraph['links']
    questlist = netgraph['questlist']
    linklist = netgraph['linklist']

    nodepositions = graphpositions(questlist, linklist)
    resultstring = netgraph['resultstring']

    print 'beflink'
    if links:
        for x in links:
            print x

    # oonvert graph to json representation for jointjs
    graphdict = graphtojson(quests, links, nodepositions, grwidth, grheight, False)
    # oonvert graph to json representation for d3
    d3dict = d3tojson(quests, links, nodepositions, grwidth, grheight, False)

    cellsjson = graphdict['cellsjson']
    keys = graphdict['keys']
    resultstring = graphdict['resultstring']

    d3jsondata = d3dict['cellsjson']




    return dict(cellsjson=XML(cellsjson), links=links, resultstring=resultstring,
                quests=quests,  keys=keys, netdebug=netdebug, d3jsondata=d3jsondata)

