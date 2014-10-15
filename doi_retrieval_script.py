#!/usr/bin/env python

import json
from search_and_DOI_utilities import plos_search, plos_dois

SEARCH_JOURNAL = "PLOS ONE"
MAX_PAPERS = 20000
search_results = plos_search(SEARCH_JOURNAL, query_type = "journal", rows = MAX_PAPERS)
print "Retrieving " + str(len(search_results)) + " DOIs from PLOS ONE..."
dois = plos_dois(search_results)
# jdois = json.dumps(dois)
doifile = open("20k_pone_dois.json", "w")
json.dump(dois, doifile)
doifile.close()
