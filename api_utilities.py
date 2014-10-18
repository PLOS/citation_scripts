#!/usr/bin/env python
# coding=utf-8

'''
api_utilities.py

Some super-basic utilities for getting useful information out of the rich citations API.
'''

import json
from urllib import quote_plus
from random import randint
import requests  # the only non-native dependency here


BASE_URL='http://api.richcitations.org/v0/'
DOIS_FILE = "apidois.json"

doifile = open(DOIS_FILE)
dois = json.load(doifile)
doifile.close()

n = len(dois)

def randdoi():
    '''Retrieves a random DOI from the list of DOIs in the API.'''
    return dois[randint(0, n-1)]

def retrieve_info(doi):
    '''
    Retrieves infomation about a DOI from the read-write API.
    This does NOT process references from a paper that hasn't previously been processed.
    It merely accesses the API for the database.
    Don't call this directly; use one of the wrapper functions below.
    '''
    url = BASE_URL + "papers?doi=" + quote_plus(doi)
    return requests.get(url)

def in_database?(doi):
    '''Does what it says on the tin.'''
    if retrieve_info(doi).status_code == 200:
        return True
    return False

def citations(doi):
    '''
    Returns citations for the given DOI, if it's a citing entity in the database.
    Otherwise, returns False.
    '''
    r = retrieve_info(doi)
    if r.status_code != 200:
        return False
    return json.loads(r.text)

