#!/usr/bin/python

import sys
import csv
import json
import pycountry
import codecs
from collections import defaultdict

class Region(object):
    def __init__(self, name, code=None, level=0, parent=None, verbose=False):
        self.name = name
        self.code = code
        self.level = level
        self.contains = []
        self.parent = parent
        try:
            self.country = pycountry.countries.get(numeric='%03d' % (int(code)))
        except:
            self.country = None
        if verbose:
            print "Created region %s in parent %s" % (name, parent)
            
    def add(self, region):
        self.contains.append(region)

    def get_countries(self):
        '''
        return list of countries (pycountry objects) in this region
        '''
        if self.country:
            return [ self.country ]
        clist = []
        for region in self.contains:
            clist += region.get_countries()
        return clist

    def includes_country(self, cc):
        '''
        Return True if this region has country with country code alpha2=cc
        '''
        if self.country is not None and self.country.alpha2==cc:
            return True
        for region in self.contains:
            if region.includes_country(cc):
                return True
        return False

    def __unicode__(self):
        return ("<[%d] " % self.level) + self.name + " in " + str(self.parent or 'None') + " >"

    __str__ = __unicode__


#cdat = csv.DictReader(codecs.open('un_world_geographic_regions.csv','rU', encoding='utf8'))
cdat = csv.DictReader(open('un_world_geographic_regions.csv','rU'))

regions = {}
regions_by_level = defaultdict(list)

current_region = Region("World", '001', 5)
verbose = True
stack = []

for cd in cdat:

    level = int(cd.get('Level', 0) or 0)
    inlevel = level
    code = cd['Numerical_code']
    name = cd['name']

    if not name:
        # skip blank
        # print "skipping %s" % cd
        continue

    if not name in regions:
        region = Region(name, code, level, parent=None)
        regions[name] = region
        regions_by_level[level].append(region)
    else:
        region = regions[name]
        level = region.level

    if level==0:	# it's a country: always add to current_region
        current_region.add(region)
        if region.parent is None:
            region.parent = current_region
    elif inlevel < 0:	# add to current_region, and don't change current_region
        print "==> Adding to current_region"
        print "Stack has %s" % map(str, stack)
        current_region.add(region)
    elif level < current_region.level:	# subregion: add, then make region the current one
        current_region.add(region)
        if region.parent is None:
            region.parent = current_region
        stack.append(current_region)	# use stack for parents
        current_region = region
    else:					# go up until at right level
        if verbose:
            print "==> Going up tree"
            print "Stack has %s" % map(str, stack)
        while current_region.level <= level:
            current_region = stack.pop()
        current_region.add(region)
        if region.parent is None:
            region.parent = current_region
        stack.append(current_region)	# use stack for parents
        current_region = region
    if verbose:
        print "   added: " + str(region)

#-----------------------------------------------------------------------------
# output csv's of countries in each region, with alpha2 country code

print "-"*77

print "France: "
print regions['France']
print "Americas: "
print regions['Americas']
print "Haiti: "
print regions['Haiti']
print
print map(str, regions['Americas'].contains)
print regions['Asia']
print map(str, regions['Asia'].contains)
print regions['Europe']
print map(str, regions['Europe'].contains)
print regions['Africa']
print map(str, regions['Africa'].contains)
print "latin america:"
print regions['Latin America and the Caribbean']
print map(str, regions['Latin America and the Caribbean'].contains)
# sys.exit(0)

def dump_region(cset, name, verbose=True):
    fn = "Countries_in_%s.csv" % name
    fp = codecs.open(fn, 'w', encoding='utf8')
    fp.write('cc, code, name\n')
    for country in cset:
        #fp.write(('%s,%s,' % (country.alpha2, country.numeric)) + country.name + '\n')
        fp.write(('%s,%s,' % (country.alpha2, country.numeric)))
        fp.write(country.name + '\n')
        #fp.write(country.alpha2 + '\n')
    fp.close()
    if verbose:
        print "Wrote %s" % fn

for level in range(4,0,-1):
    print "Regions in Level %d: " % level
    for r in regions_by_level[level]:
        print "    %s" % r
        dump_region(r.get_countries(), r.name, verbose=False)

#-----------------------------------------------------------------------------
# Africa

print "-"*77
print "Countries in Africa:"
# cset = [ dict(name=x.name, cc=x.alpha2) for x in regions['Africa'].get_countries() ]
# print json.dumps(cset, indent=2)
dump_region(regions['Africa'].get_countries(), 'Africa')

#-----------------------------------------------------------------------------
# Least developed countries

print "-"*77
rname = "Least developed countries"
print "Countries in %s:" % rname
#cset = [ dict(name=x.name, cc=x.alpha2) for x in regions[rname].get_countries() ]
#print json.dumps(cset, indent=2)
dump_region(regions[rname].get_countries(), rname)

#-----------------------------------------------------------------------------
# developing nations

rnames = ['Africa', 'Americas', 'Caribbean', 'Central America', 'South America', 'Asia', 'Oceania']

rset = set()
for rname in rnames:
    rset = rset.union(set(regions[rname].get_countries()))
    dump_region(regions[rname].get_countries(), rname)

# remove northern america, Japan, Australia, New Zealand

northam = regions['Northern America'].get_countries()

rset = rset.difference(northam)
rset = rset.difference(regions['Japan'].get_countries())
rset = rset.difference(regions['Australia'].get_countries())
rset = rset.difference(regions['New Zealand'].get_countries())

dump_region(rset, 'Developing_Nations')

#-----------------------------------------------------------------------------
# sub-saharan africa = Africa - Northern Africa + Sudan

rnames = ['Africa']

rset = set()
for rname in rnames:
    rset = rset.union(set(regions[rname].get_countries()))

rset = rset.difference(regions['Northern Africa'].get_countries())
rset = rset.union(set(regions['Sudan'].get_countries()))

dump_region(rset, 'Sub-Saharan-Africa')
