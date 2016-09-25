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

import time
import pycountry
from incf.countryutils import transformations

@auth.requires_membership('manager')
def countries():
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


def subdivns():
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
    
@auth.requires_membership('manager')
def subdivns_old():
    # Unspecified Subdivision is already added - and not now adding this to every country
    # More of these can be got from http://www.unece.org/cefact/locode/subdivisions.html

    subdivs = [[{'Country': 'Canada (NA)'}, ['Alberta', 'British Columbia', 'Manitoba', 'New Brunswick',
                                             'Newfoundland and Labrador', 'Nova Scotia', 'Ontario',
                                             'Prince Edward Island', 'Quebec',
                                             'Saskatchewan']],
               [{'Country': 'United States (NA)'}, ['Alabama', 'Alaska', 'American Samoa',
                                                    'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
                                                    'Delaware', 'District of Columbia',
                                                    'Florida', 'Georgia', 'Guam', 'Hawaii', 'Idaho', 'Illinois',
                                                    'Indiana',
                                                    'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
                                                    'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
                                                    'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
                                                    'New Jersey', 'New Mexico', 'New York',
                                                    'North Carolina', 'North Dakota', 'Northern Mariana Islands',
                                                    'Ohio', 'Oklahoma', 'Oregon',
                                                    'Pennsylvania', 'Puerto Rico', 'Rhode Island', 'South Carolina',
                                                    'South Dakota', 'Tennessee',
                                                    'Texas', 'U.S. Virgin Islands', 'Utah', 'Vermont', 'Virginia',
                                                    'Washington',
                                                    'West Virginia', 'Wisconsin', 'Wyoming']],
               [{'Country': 'United Kingdom (EU)'}, ['England', 'Northern Ireland', 'Scotland', 'Wales']]]

    for x in subdivs:
        countryname = x[0]['Country']
        for y in x[1]:
            if db(db.subdivision.subdiv_name == y).isempty():
                db.subdivision.insert(subdiv_name=y, country=countryname)

    setup_complete = db(db.initialised.id > 0).update(website_init=True)
    time.sleep(1)
    # this should refresh after update
    INIT = db(db.initialised).select().first()
    return locals()


@auth.requires_membership('manager')
def countries_old():
    continents = ["Unspecified", "Africa (AF)", "Asia (AS)", "Europe (EU)", "North America (NA)", "Oceania (OC)",
                  "South America (SA)"]
    for x in continents:
        if db(db.continent.continent_name == x).isempty():
            db.continent.insert(continent_name=x)

    countrys = [[{'Continent': 'Africa (AF)'}, ['Algeria (AF)', 'Angola (AF)', 'Benin (AF)', 'Botswana (AF)',
                                                'Burkina (AF)', 'Burundi (AF)', 'Cameroon (AF)', 'Cape Verde (AF)',
                                                'Central African Republic (AF)', 'Chad (AF)', 'Comoros (AF)',
                                                'Congo (AF)',
                                                'Congo, Democratic Republic of (AF)', 'Djibouti (AF)', 'Egypt (AF)',
                                                'Equatorial Guinea (AF)', 'Eritrea (AF)', 'Ethiopia (AF)', 'Gabon (AF)',
                                                'Gambia (AF)', 'Ghana (AF)', 'Guinea (AF)', 'Guinea-Bissau (AF)',
                                                'Ivory Coast (AF)', 'Kenya (AF)', 'Lesotho (AF)', 'Liberia (AF)',
                                                'Libya (AF)',
                                                'Madagascar (AF)', 'Malawi (AF)', 'Mali (AF)', 'Mauritania (AF)',
                                                'Mauritius (AF)', 'Morocco (AF)', 'Mozambique (AF)', 'Namibia (AF)',
                                                'Niger (AF)',
                                                'Nigeria (AF)', 'Rwanda (AF)', 'Sao Tome and Principe (AF)',
                                                'Senegal (AF)', 'Seychelles (AF)', 'Sierra Leone (AF)', 'Somalia (AF)',
                                                'South Africa (AF)', 'South Sudan (AF)', 'Sudan (AF)', 'Swaziland (AF)',
                                                'Tanzania (AF)', 'Togo (AF)', 'Tunisia (AF)', 'Uganda (AF)',
                                                'Zambia (AF)', 'Zimbabwe (AF)']],
                [{'Continent': 'Asia (AS)'}, ['Afghanistan (AS)', 'Bahrain (AS)', 'Bangladesh (AS)', 'Bhutan (AS)',
                                              'Brunei (AS)', 'Burma (Myanmar) (AS)', 'Cambodia (AS)',
                                              'China (AS)', 'East Timor (AS)', 'India (AS)', 'Indonesia (AS)',
                                              'Iran (AS)', 'Iraq (AS)',
                                              'Israel (AS)', 'Japan (AS)', 'Jordan (AS)',
                                              'Kazakhstan (AS)', 'Korea, North (AS)', 'Korea, South (AS)',
                                              'Kuwait (AS)',
                                              'Kyrgyzstan (AS)', 'Laos (AS)', 'Lebanon (AS)', 'Malaysia (AS)',
                                              'Maldives (AS)', 'Mongolia (AS)', 'Nepal (AS)', 'Oman (AS)',
                                              'Pakistan (AS)',
                                              'Philippines (AS)', 'Qatar (AS)', 'Russian Federation (AS)',
                                              'Saudi Arabia (AS)', 'Singapore (AS)', 'Sri Lanka (AS)', 'Syria (AS)',
                                              'Tajikistan (AS)', 'Thailand (AS)', 'Turkey (AS)', 'Turkmenistan (AS)',
                                              'United Arab Emirates (AS)', 'Uzbekistan (AS)', 'Vietnam (AS)',
                                              'Yemen (AS)']],
                [{'Continent': 'Europe (EU)'}, ['Albania (EU)', 'Andorra (EU)', 'Armenia (EU)', 'Austria (EU)',
                                                'Azerbaijan (EU)', 'Belarus (EU)', 'Belgium (EU)',
                                                'Bosnia and Herzegovina (EU)', 'Bulgaria (EU)', 'Croatia (EU)',
                                                'Cyprus (EU)',
                                                'Czech Republic (EU)', 'Denmark (EU)', 'Estonia (EU)',
                                                'Finland (EU)', 'France (EU)', 'Georgia (EU)', 'Germany (EU)',
                                                'Greece (EU)',
                                                'Hungary (EU)', 'Iceland (EU)', 'Ireland (EU)', 'Italy (EU)',
                                                'Latvia (EU)', 'Liechtenstein (EU)', 'Lithuania (EU)',
                                                'Luxembourg (EU)',
                                                'Macedonia (EU)', 'Malta (EU)', 'Moldova (EU)', 'Monaco (EU)',
                                                'Montenegro (EU)', 'Netherlands (EU)', 'Norway (EU)', 'Poland (EU)',
                                                'Portugal (EU)',
                                                'Romania (EU)', 'San Marino (EU)', 'Serbia (EU)',
                                                'Slovakia (EU)', 'Slovenia (EU)', 'Spain (EU)', 'Sweden (EU)',
                                                'Switzerland (EU)',
                                                'Ukraine (EU)', 'United Kingdom (EU)', 'Vatican City (EU)']],
                [{'Continent': 'North America (NA)'}, ['Antigua and Barbuda (NA)', 'Bahamas (NA)',
                                                       'Barbados (NA)', 'Belize (NA)', 'Canada (NA)', 'Costa Rica (NA)',
                                                       'Cuba (NA)', 'Dominica (NA)', 'Dominican Republic (NA)',
                                                       'El Salvador (NA)',
                                                       'Grenada (NA)', 'Guatemala (NA)', 'Haiti (NA)', 'Honduras (NA)',
                                                       'Jamaica (NA)', 'Mexico (NA)', 'Nicaragua (NA)', 'Panama (NA)',
                                                       'Saint Kitts and Nevis (NA)',
                                                       'Saint Lucia (NA)', 'Saint Vincent and the Grenadines (NA)',
                                                       'Trinidad and Tobago (NA)', 'United States (NA)']],
                [{'Continent': 'Oceania (OC)'}, ['Australia (OC)', 'Fiji (OC)', 'Kiribati (OC)',
                                                 'Marshall Islands (OC)', 'Micronesia (OC)', 'Nauru (OC)',
                                                 'New Zealand (OC)', 'Palau (OC)', 'Papua New Guinea (OC)',
                                                 'Samoa (OC)',
                                                 'Solomon Islands (OC)', 'Tonga (OC)', 'Tuvalu (OC)', 'Vanuatu (OC)']],
                [{'Continent': 'South America (SA)'}, ['Argentina (SA)', 'Bolivia (SA)',
                                                       'Brazil (SA)', 'Chile (SA)', 'Colombia (SA)', 'Ecuador (SA)',
                                                       'Guyana (SA)', 'Paraguay (SA)', 'Peru (SA)', 'Suriname (SA)',
                                                       'Uruguay (SA)', 'Venezuela (SA)']]]

    for x in countrys:
        contname = x[0]['Continent']
        for y in x[1]:
            if db(db.country.country_name == y).isempty():
                db.country.insert(country_name=y, continent=contname)

    return locals()
