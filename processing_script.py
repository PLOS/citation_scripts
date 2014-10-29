#!/usr/bin/env python
# coding=utf-8

from __future__ import division
import json
import traceback, sys
import time
from xml_parsing import parse_XML_list
from citation_validation import validate, multi_validate
from email_alert import email, text

DOIS_FILE = "final_run_plos_dois.json"
DB_DIR = "final_dbs/"
DB_FILE_PREFIX = DB_DIR + "final_db_"
N = 74563 # number of papers to process.
OFFSET = 0 # where to start in the list of DOIs

CACHING_INTERVAL = 100

doifile = open(DOIS_FILE)
dois = json.load(doifile)
doifile.close()

run_dois = dois[OFFSET:OFFSET+N]

c = OFFSET//CACHING_INTERVAL
tot, proc, refs, ratio = multi_validate("pone_dbs/pone_db_", (0, 350))

t0 = time.time()

try:
    x = 0
    papers_processed = 0 + proc
    uri_ratio = [0 + ratio, 0 + refs]  # first number is the ratio for all references processed to this point; second is the number of references processed (as opposed to the papers processed).
    print "Previously attempted to process " + str(tot) + " papers so far; retrieved at least " + str(papers_processed) + "; URI ratio is " + str(round(uri_ratio[0], 3)) + " for " + str(uri_ratio[1]) + " end-of-paper references processed thus far."
    print "Starting a run of " + str(N) + " papers."
    print "Results from this run will be deposited into " + DB_DIR + ". If that directory doesn't exist, fix that right now."
    
    text("Starting a run of " + str(N) + " papers.")

    while x < N-1:
        runlist = run_dois[x:x+CACHING_INTERVAL]
        rc_list = parse_XML_list(runlist)

        print "Dumping data into file..."
        filename = DB_FILE_PREFIX + str(c) + ".json"
        dbfile = open(filename, "w")
        json.dump(rc_list, dbfile)
        dbfile.close()

        print "Validating results..."
        try:
            results = validate(filename)
        except:
            subj = "Validation failed with error " + str(sys.exc_info()[0]) + "!"
            body = "Somewhere around " + str(x) + " papers were attempted, with at least " + str(papers_processed) + " successfully processed. The last file written was " + filename + ". Error traceback follows: \n" + str(traceback.format_exc())
            print subj, body
            email('abecker@plos.org', subj, body)
        else:
            subject = "Code finished but not all papers were retrieved"
            papers_processed += results[1][0]
            if results[0]:
                print "Retrieval succeeded for all papers!"
                subject = "Code ran successfully for all papers!"
            #     papers_processed += len(runlist)
            #     uri_ratio[0] = (uri_ratio[0]*uri_ratio[1] + results[1]*results[2])/(uri_ratio[1] + results[2])
            #     uri_ratio[1] += results[2]
            # else:
            # papers_processed += results[1][0]
            elif not results[2][2]:
                subj = "Some badly formed JSON was returned!"
                body = "Somewhere around " + str(x + len(runlist)) + " papers were attempted, with at least " + str(papers_processed) + " successfully processed. The last file written was " + filename + "."
                print subj, body
                email('abecker@plos.org', subj, body)
            uri_ratio[0] = (uri_ratio[0]*uri_ratio[1] + results[2][0]*results[2][1])/(uri_ratio[1] + results[2][1])
            uri_ratio[1] += results[2][1]
            # if not results[2][2]:
            #     subj = "Some badly formed JSON was returned!"
            #     body = "Somewhere around " + str(x + len(runlist)) + " papers were attempted, with at least " + str(papers_processed) + " successfully processed. The last file written was " + filename + "."
            #     print subj, body
            #     email('abecker@plos.org', subj, body)
            for r in results[3:]:
                print r
            update_string = "Attempted to process " + str(x + len(runlist) + tot) + " papers so far; retrieved at least " + str(papers_processed) + "; URI ratio is " + str(round(uri_ratio[0], 3)) + " for " + str(uri_ratio[1]) + " end-of-paper references processed."
            print update_string

        c += 1

        if not c%100:
            text("Still working!" + update_string)

        x = x+CACHING_INTERVAL
    
    t1 = time.time()
    dt = t1 - t0
    s = "Attempted to process " + str(N) + " papers in " + str(dt) + " seconds; retrieved at least " + str(papers_processed - proc) + "; total URI ratio is " + str(round(uri_ratio[0], 3)) + " for " + str(uri_ratio[1]) + " end-of-paper references processed."
    print s
    email('abecker@plos.org', subject, s)

except:
    print "Whoops, code stopped because of an error!"
    e = "Somewhere around " + str(x + tot) + " papers were attempted, with at least " + str(papers_processed) + " successfully processed."
    print e
    email('abecker@plos.org',
            "Code failed with error " + str(sys.exc_info()[0]) + "!",
            e + " Error traceback follows: \n" + str(traceback.format_exc())
            )
    raise
