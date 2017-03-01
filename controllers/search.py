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
#
# search is now using the haystack plugin and generating a full text index on question text only
# which we might add a capabilty to filter by action or question
# it will allow generation of a list of up to x items to display the questions and status which I
# think may just be another method of populating the existing review function
# so looks like the in operator would work for this - but most likely search is different and we keep
# as separate function to begin with until requirements fully understood
# but by some means search will get a list of 20 items (which may be hard coded) GQL is limited to 
# 30 and then go and retrieve the related ids so will always be two queries one on the full text search
# which probably needs a bit of further understanding on my part
# and then a second one to get the questions which would have pagination I think
#
# pagination to be added here at some point but currently search limit of 20 and refine search will do
# aiming to now support 3 searches and default will be a google simple search


@auth.requires(True, requires_login=requires_login)
def newsearch():
    fields = ['searchstring', 'linklevels']
    form = SQLFORM(db.viewscope, fields=fields)
    results = None

    if form.validate():
        query = indsearch.search(questiontext=form.vars.searchstring)
        results = db(query).select()
        session.searchstring = form.vars.searchstring
    if results:
        session.networklist = [x.id for x in results]
    else:
        session.networklist = []
    count = len(session.networklist)
    return dict(form=form, results=results, count=count, linklevels=form.vars.linklevels)

@auth.requires_membership('manager')
def delindex():
    results = indsearch.index_delete('qtype', 'questiontext')
    message = 'question index deleted'
    return dict(message=message, results=results)

@auth.requires_membership('manager')
def reindex():
    rows = db(db.question.id > 0).select()
    for row in rows:
        indsearch.index_create(row, row.id)
    message = 'question index recreated'
    return dict(message=message)
