#!/usr/bin/env python
# coding=utf-8

import json
import time
import requests  # the only non-native dependency here


BASE_URL='http://xmlapi.richcitations.org/v0/'
PAPER_URL='%spaper'%(BASE_URL)
DELAY = 2 # delay between API calls on a 202 status, in seconds
GIVE_UP_202 = 2 # number of times to receive a 202 status before temporarily giving up
ACTUALLY_GIVE_UP = 2 # number of times to repeat the cycle before truly giving up on a paper


def retrieve(raw_doi, run_dois, retrying = False, index_list = None):
    '''
    Retrieves rich citation information for a single DOI from a list of DOIs.
    Don't call this function directly -- use retrieval() instead.
    '''
    if index_list:
        i = index_list.index(raw_doi) + 1
        n = len(index_list)
    else:
        i = run_dois.index(raw_doi) + 1
        n = len(run_dois)
    doi = "http://dx.doi.org/%s"%(raw_doi)
    response = requests.get(PAPER_URL, params={'id': doi})
    replies_202 = 1
    while response.status_code == 202:
        if replies_202 > GIVE_UP_202:
            return {"result":False, "doi":raw_doi}
        response = requests.get(PAPER_URL, params={'id': doi})
        print "Retrieving citations from paper", i, "out of", n, "..."
        replies_202 += 1
        time.sleep(DELAY)
    if response.status_code == 200:
        try:
            parsed = json.loads(response.text)
        except ValueError:
            print "Bad JSON returned! Let's just say that paper failed. Maybe we'll try it again later..."
            return {"result":False, "doi":raw_doi}
        print "Citations retrieved for paper", i, "out of", n, "!"
        if retrying:
            run_dois.remove(raw_doi)
        return {"result":parsed, "doi":raw_doi}
    else:
        print response
        return {"result":False, "doi":raw_doi}


def retrieval(doi_list):
    '''
    Retrieves rich citation information for a given list of DOIs.
    '''
    n = len(doi_list)
    print "Attempting to retrieve citation information for", n, "papers."
    t0 = time.time()
    rc_list = [retrieve(doi, doi_list) for doi in doi_list]
    retry = [i["doi"] for i in rc_list if not i["result"]] # gives us the list we need for retrying.
    rc_list = [i for i in rc_list if i["result"]] # gets rid of the Falses
    for i in range(ACTUALLY_GIVE_UP):
        print "Retrying papers!"
        extra_list = [retrieve(doi, retry, retrying = True, index_list = doi_list) for doi in retry[:]]
        if i < ACTUALLY_GIVE_UP - 1:
            extra_list = [i for i in extra_list if i["result"]]
        rc_list.extend(extra_list)
    t1 = time.time()
    dt = t1-t0
    print "Retrieved citations for", n, "papers in", dt, "seconds."
    return rc_list
