#!/usr/bin/env python

import json
from search_and_DOI_utilities import plos_search, plos_dois


# THIS DOES NOT WORK. DO NOT RUN IT.

# SEARCH_JOURNAL = "PLOS ONE"
MAX_PAPERS = 1015
extra_parameters = {'journal': 'PLOS Medicine'}

search_results = plos_search('*', query_parameters=extra_parameters, rows=MAX_PAPERS)
# search_results = plos_search('*', rows=MAX_PAPERS)
print "Retrieving " + str(len(search_results)) + " DOIs from PLOS..."
dois = plos_dois(search_results)
# jdois = json.dumps(dois)
doifile = open("temp.json", "w")
json.dump(dois, doifile)
doifile.close()
