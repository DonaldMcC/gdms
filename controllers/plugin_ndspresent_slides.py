# coding: utf8
# 尝试
def index(): return dict(message="hello from seo.py")

def split():
    presentation = db(db.presentation.name==request.args[0]).select().first()
    splitted = presentation.markmin.split("<!--- slide --->")
    db(db.slide.presentation_id==presentation.id).delete()
    
    for n, markmin in enumerate(splitted):
        db.slide.insert(
            presentation_id=presentation.id,
            markmin=markmin,
            )
    return dict(n=n)
    
def show():
    ""
    presentation = db(db.presentation.name==request.args[0]).select().first()
    slides = db(db.slide.presentation_id==presentation.id).select()
    
    response.title = presentation.title
    response.description = presentation.description
    response.keywords = presentation.keywords
    response.author = presentation.author

    return dict(slides=slides)
