#!/usr/bin/python
#
# make CSV table of geographic regions, with each row being a country, and 
# columns being cc, code, name, continent, econ_group, un_region, special_region1, developing_nation
#
# continent: africa, americas, asia, europe, ocenia
# econ_group: least_developed, landlocked_developing, small_island_developing
# un_region: all listed in http://unstats.un.org/unsd/methods/m49/m49regin.htm
# spcial_region: Sub-Saharan Africa
#
# note that a country can be in multiple regional units, and thus each of the
# regional unit columns is chosen to be dichotomies.

import sys
import json
import unicodecsv as csv
from collections import defaultdict

ofn = "geographic_regions_by_country.csv"

#-----------------------------------------------------------------------------

continents = ['data/Countries_in_Africa.csv',
              'data/Countries_in_Americas.csv',
              'data/Countries_in_Asia.csv',
              'data/Countries_in_Europe.csv',
              'data/Countries_in_Oceania.csv',
]

un_regions = ['data/Countries_in_Caribbean.csv',
           'data/Countries_in_Central America.csv',
           'data/Countries_in_Central Asia.csv',
           'data/Countries_in_Eastern Africa.csv',
           'data/Countries_in_Eastern Asia.csv',
           'data/Countries_in_Eastern Europe.csv',
           'data/Countries_in_Melanesia.csv',
           'data/Countries_in_Micronesia.csv',
           'data/Countries_in_Middle Africa.csv',
           'data/Countries_in_Northern Africa.csv',
           'data/Countries_in_Northern America.csv',
           'data/Countries_in_Northern Europe.csv',
           'data/Countries_in_Polynesia.csv',
           'data/Countries_in_South America.csv',
           'data/Countries_in_South-Eastern Asia.csv',
           'data/Countries_in_Southern Africa.csv',
           'data/Countries_in_Southern Asia.csv',
           'data/Countries_in_Southern Europe.csv',
           'data/Countries_in_Western Africa.csv',
           'data/Countries_in_Western Asia.csv',
           'data/Countries_in_Western Europe.csv',
]

econ_groups = [
           'data/Countries_in_Developed regions.csv',
           'data/Countries_in_Developing_Nations.csv',
           ]

developing_nations = [
           'data/Countries_in_Least developed countries.csv',
           # 'data/Countries_in_Landlocked developing countries.csv',
           # 'data/Countries_in_Small island developing States.csv',
]

special_regions1 = [
    'data/Countries_in_Latin America and the Caribbean.csv',
    'data/Countries_in_Sub-Saharan-Africa.csv',
]

#-----------------------------------------------------------------------------

countries = {}

def mark_countries_in_region(fn, colname):
    '''
    Read in CSV file, find countries, mark them as such in the countries dict
    extract region name from filename fn.
    '''
    rname = fn.split('Countries_in_', 1)[1].split('.csv',1)[0]
    for row in csv.DictReader(open(fn)):
        cc = row['cc']
        if cc not in countries:
            cdat = {'cc': cc, 'code': row[' code'], 'name': row[' name']}
            countries[cc] = cdat
        else:
            cdat = countries[cc]
        if colname in cdat:
            print "Error!  Collision in region %s, file %s, cc=%s (had col %s = region %s)" % (rname, fn, cc, colname, cdat[colname])
            sys.stdout.flush()
        cdat[colname] = rname

fields = ['cc', 'code', 'name']

all_regions = [{'region_name': 'UN defined Continents',
                'files': continents,
                'colname': 'continent'},
               {'region_name': 'UN defined sub-continent major geographic regions',
                'files': un_regions,
                'colname': 'un_region'},
               {'region_name': 'UN defined major geographical economic groups (developing and developed nations)',
                'files': econ_groups,
                'colname': 'econ_group'},
               {'region_name': 'UN defined developing nation groups',
                'files': developing_nations,
                'colname': 'developing_nation'},
               {'region_name': 'Special Regions Set 1',
                'files': special_regions1,
                'colname': 'special_region1'},
               ]

# all regions

for rdat in all_regions:
    fields.append(rdat['colname'])
    for rfn in rdat['files']:
        mark_countries_in_region(rfn, rdat['colname'])

# output data

dw = csv.DictWriter(open(ofn, 'w'), fieldnames=fields)
dw.writeheader()
cnt = 0
for cdat in countries.values():
    dw.writerow(cdat)
    cnt += 1

print "Wrote %d rows to %s" % (cnt, ofn)

# write out schema file in json

sfn = ofn.replace('.csv', '-schema.json')
schema = [
    {'type': 'STRING',
     'name': 'cc',
     'description': 'ISO two-letter country code' },
    {'type': 'INTEGER',
     'name': 'code',
     'description': 'UN country code number' },
    {'type': 'STRING',
     'name': 'name',
     'description': 'UN designated country full name'},
]

for rdat in all_regions:
    desc = rdat['region_name']
    rf = [x.split('Countries_in_', 1)[1] for x in rdat['files']]
    if len(rf)<8:
        desc += ' files: %s' % (','.join(rf))
    sent = {'type': 'STRING',
            'name': rdat['colname'],
            'description': desc}
    schema.append(sent)

open(sfn, 'w').write(json.dumps(schema, indent=4))
print "Wrote schema to %s" % sfn

print "Load this into BigQuery using a command like:"
print "bq load --skip_leading_rows=1 --replace --project_id PROJECT_ID geocode.geographic_regions_by_country geographic_regions_by_country.csv geographic_regions_by_country-schema.json"
