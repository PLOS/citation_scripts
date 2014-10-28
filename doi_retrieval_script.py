#!/usr/bin/env python

import json
from search_and_DOI_utilities import plos_search, plos_dois


THIS DOES NOT WORK. DO NOT RUN IT.

SEARCH_JOURNAL = "PLOS ONE"
MAX_PAPERS = 120000
extra_parameters = {'journal': 'PLOS ONE'}

search_results = plos_search('*', extra_parameters=extra_parameters, rows=MAX_PAPERS)
print "Retrieving " + str(len(search_results)) + " DOIs from PLOS ONE..."
dois = plos_dois(search_results)
# jdois = json.dumps(dois)
doifile = open("pone_dois.json", "w")
json.dump(dois, doifile)
doifile.close()
