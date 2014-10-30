#!/usr/bin/env python
# coding=utf-8


'''
xml_parsing.py

Utilities for using the XML parsing API.
'''

import json
import time
from multiprocessing import Pool
import requests  # the only non-native dependency here

BASE_URL='http://xmlapi.richcitations.org/v0/'
PAPER_URL='%spaper'%(BASE_URL)
DELAY = 0 # delay between API calls on a non-200 status, in seconds
BATCH_DELAY_PER_PAPER = 1.2 # delay per paper between sending a batch of papers for processing and retrying the batch, in seconds
GIVE_UP_202 = 0 # number of times to receive a 202 status before temporarily giving up
ACTUALLY_GIVE_UP = 2 # number of times to repeat the cycle before truly giving up on a paper


def parse_XML(raw_doi, run_dois, retrying = False, index_list = None):
    '''
    Sends a single DOI from a list of DOIs to the XML parsing API.
    Don't call this function directly -- use parse_XML_list() instead.
    '''
    if index_list:
        i = index_list.index(raw_doi) + 1
        n = len(index_list)
    else:
        i = run_dois.index(raw_doi) + 1
        n = len(run_dois)
    doi = "http://dx.doi.org/%s"%(raw_doi)
    print "Requesting citations for paper", i, "out of", n, "..."
    try:
        response = requests.get(PAPER_URL, params={'id': doi})
    except ConnectionError:
        print "Problem with the connection. We'll try that one again later."
        return {"result":False, "doi":raw_doi}
    replies_202 = 1
    while response.status_code == 202:
        if replies_202 > GIVE_UP_202:
            return {"result":False, "doi":raw_doi}
        response = requests.get(PAPER_URL, params={'id': doi})
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
        time.sleep(DELAY) # to give the APIs (ours, CrossRef's) some time before we hit them again when they're having problems.


class XMLParser(object):
    '''
    A function object wrapping parse_XML().
    We need this for multiprocessing.
    Specifically, Pool.map can't handle lambdas, so this is in place of a lambda.
    Never create an instance of this directly -- use parse_XML_list().
    '''
    def __init__(self, list, retrying = False, index_list = None):
        self.list = list
        self.retrying = retrying
        self.index_list = index_list
    def __call__(self, doi):
        return parse_XML(doi, self.list, retrying = self.retrying, index_list = self.index_list)


def parse_XML_multiprocessing(doi_list, retrying = False, index_list = None):
    '''
    Nearly the same as parse_XML(), but with multiprocessing over the entire list of DOIs.
    Don't call this directly to process a whole list -- call parse_XML_list() instead.
    '''
    n = len(doi_list)
    p = Pool(n)
    rc_list = p.map(XMLParser(doi_list, retrying = retrying, index_list = index_list), doi_list)
    p.close()
    return rc_list

def parse_XML_list(doi_list):
    '''
    Sends a given list of DOIs to the XML parsing API.
    '''
    n = len(doi_list)
    print "Attempting to retrieve citation information for", n, "papers."
    t0 = time.time()
    rc_list = parse_XML_multiprocessing(doi_list)
    # rc_list = [parse_XML(doi, doi_list) for doi in doi_list]
    retry = [i["doi"] for i in rc_list if not i["result"]] # gives us the list we need for retrying.
    rc_list = [i for i in rc_list if i["result"]] # gets rid of the Falses
    for i in range(ACTUALLY_GIVE_UP):
        num_retries = len(retry)
        batch_delay = BATCH_DELAY_PER_PAPER * num_retries
        print "Waiting", batch_delay, "seconds before retrying..."
        time.sleep(batch_delay)
        print "Retrying papers!"
        # extra_list = parse_XML_multiprocessing(retry, retry[:], retrying = True, index_list = doi_list)
        extra_list = [parse_XML(doi, retry, retrying = True, index_list = doi_list) for doi in retry[:]]
        if i < ACTUALLY_GIVE_UP - 1:
            extra_list = [i for i in extra_list if i["result"]]
        rc_list.extend(extra_list)
    t1 = time.time()
    dt = t1-t0
    print "Retrieved citations for", n, "papers in", dt, "seconds."
    return rc_list
