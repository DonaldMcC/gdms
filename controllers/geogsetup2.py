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

# This will replace geogsetup in due course and use the https://pypi.python.org/pypi/incf.countryutils
# the pycountry libary will then be used to setup the subdivisions and https://pypi.python.org/pypi/pycountry 

import time
import pycountry
from incf.countryutils import transformations
def countrytest():
    continents = {"Unspecified"}
    print pycountry.countries
    for country in pycountry.countries:
        try:
            continents.add(transformations.cn_to_ctn(country.name))
        except KeyError, e:
            print 'KeyError - reason "%s"' % str(e)
            
    for x in continents:
        if db(db.continent.continent_name == x).isempty():
            db.continent.insert(continent_name=x)
            
    for country in pycountry.countries:
        try:  # seems som
            continent = transformations.cn_to_ctn(country.name)
            if db(db.country.country_name == country).isempty():
                db.country.insert(country_name=country.name, continent=continent)  
                print 'Inserted country'
        except KeyError, e:
            print 'IKeyError - reason "%s"' % str(e)
            
    return locals()


def subdivntest():
    for country in pycountry.countries:
        try: 
            subdivns = pycountry.subdivisions.get(country_code=country.alpha2)
            for x in subdivns:
                if db(db.subdivision.subdiv_name == x.name).isempty():
                    db.subdivision.insert(subdiv_name=x.name, country=country.name)
        except KeyError, e:
            print 'I got a KeyError - reason "%s"' % str(e)
            
    setup_complete = db(db.initialised.id > 0).update(website_init=True)
    INIT = db(db.initialised).select().first()       
    return locals()
    
