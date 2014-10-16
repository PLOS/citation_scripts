#!/usr/bin/env python
# coding=utf-8

from __future__ import division
import json
import traceback, sys
from citation_retrieval import retrieval
from citation_validation import validate
# from email_alert import email, text

DOIS_FILE = "20k_pone_dois.json"
DB_FILE_PREFIX = "pone_dbs/pone_db_8000_to_9000_"
N = 1000 # number of papers to test things out on.
OFFSET = 8000 # where to start in the list of DOIs

CACHING_INTERVAL = 500

doifile = open(DOIS_FILE)
dois = json.load(doifile)
doifile.close()

run_dois = dois[OFFSET:OFFSET+N]


try:
    x = 0
    c = 0
    papers_processed = 0
    uri_ratio = [0, 0]  # first number is the ratio for all references processed to this point; second is the number of references processed (as opposed to the papers processed).

    print "Results from this run will be deposited into " + DB_FILE_PREFIX + ". If that directory doesn't exist, fix that right now."

    # text("Starting a run of " + str(N) + " papers.")

    while x < N-1:
        runlist = run_dois[x:x+CACHING_INTERVAL]
        rc_list = retrieval(runlist)

        print "Dumping data into file..."
        filename = DB_FILE_PREFIX + str(c) + ".json"
        dbfile = open(filename, "w")
        json.dump(rc_list, dbfile)
        dbfile.close()

        print "Validating results..."
        results = validate(filename)
        subject = "Code finished but not all papers were retrieved"
        if results[0]:
            print "Retrieval succeeded for all papers!"
            subject = "Code ran successfully for all papers!"
            papers_processed += len(runlist)
            uri_ratio[0] = (uri_ratio[0]*uri_ratio[1] + results[1]*results[2])/(uri_ratio[1] + results[2])
            uri_ratio[1] += results[2]
        else:
            papers_processed += results[1][0]
            uri_ratio[0] = (uri_ratio[0]*uri_ratio[1] + results[2][0]*results[2][1])/(uri_ratio[1] + results[2][1])
            uri_ratio[1] = results[2][1]
        for r in results[3:]:
            print r
        update_string = "Attempted to process " + str(x + len(runlist)) + " papers so far; retrieved " + str(papers_processed) + "; URI ratio is " + str(round(uri_ratio[0], 3)) + "."
        print update_string

        c += 1

        # if not c%4:
        #     text("Still working!" + update_string)

        x = x+CACHING_INTERVAL

    s = "Attempted to process " + str(N) + " papers; retrieved " + str(papers_processed) + "; total URI ratio is " + str(round(uri_ratio[0], 3)) + " for " + str(uri_ratio[1]) + " end-of-paper references processed."
    print s
    # email('abecker@plos.org', subject, s)

except:
    print "Whoops, code stopped because of an error!"
    e = "Somewhere around " + str(x) + " papers were attempted, with at least " + str(papers_processed) + " successfully processed."
    print e
    # email('abecker@plos.org',
    #         "Code failed with error " + str(sys.exc_info()[0]) + "!",
    #         e + " Error traceback follows: \n" + str(traceback.format_exc())
    #         )
    raise
