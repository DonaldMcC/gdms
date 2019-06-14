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
from pycountry_convert import country_alpha2_to_continent_code as cont_lookup
#  will now create dictionary of continents and add the value NA OC AF EU SA AN AS

@auth.requires_membership('manager')
def countries():
    continentdict = {
        'UN': 'Unspecified',
        'NA': 'North America',
        'SA': 'South America',
        'AS': 'Asia',
        'EU': 'Europe',
        'OC': 'Oceania',
        'AF': 'Africa',
        'AN': 'Antartica'
    }

    for x in continentdict.values():
        if db(db.continent.continent_name == x).isempty():
            db.continent.insert(continent_name=x)
            
    for country in pycountry.countries:
        try:  # seems som
            continent = continentdict[cont_lookup(country.alpha_2)]
            if db(db.country.country_name == country).isempty():
                db.country.insert(country_name=country.name, continent=continent)
        except KeyError as e:
            print('IKeyError - reason "%s"' % str(e))
            
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
            print('I got a KeyError - reason "%s"' % str(e))
            
    setup_complete = db(db.initialised.id > 0).update(website_init=True)
    INIT = db(db.initialised).select().first()       
    return locals()
