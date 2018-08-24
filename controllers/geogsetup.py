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

# This is still inelegant but it only runs once so it will do for now
# Lets change to a 2 dim list
# need to pip install pycountry and incf.countryutils before this code will work
# incf.countryutils is not quite python 3 compatible


import pycountry
from incf.countryutils import transformations


@auth.requires_membership('manager')
def countries():
    continents = {"Unspecified"}
    for country in pycountry.countries:
        try:
            continents.add(transformations.cn_to_ctn(country.name))
        except KeyError as e:
            print ('KeyError - reason "%s"' % str(e))
            
    for x in continents:
        if db(db.continent.continent_name == x).isempty():
            db.continent.insert(continent_name=x)
            
    for country in pycountry.countries:
        try:  # seems som
            continent = transformations.cn_to_ctn(country.name)
            if db(db.country.country_name == country).isempty():
                db.country.insert(country_name=country.name, continent=continent)
        except KeyError as e:
            print ('IKeyError - reason "%s"' % str(e))
            
    return locals()


@auth.requires_membership('manager')
def subdivns():
    for country in pycountry.countries:
        try: 
            subdivns = pycountry.subdivisions.get(country_code=country.alpha_2)
            for x in subdivns:
                if db(db.subdivision.subdiv_name == x.name).isempty():
                    db.subdivision.insert(subdiv_name=x.name, country=country.name)
        except KeyError as e:
            print ('I got a KeyError - reason "%s"' % str(e))
            
    setup_complete = db(db.initialised.id > 0).update(website_init=True)
    INIT = db(db.initialised).select().first()       
    return locals()