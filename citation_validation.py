#!/usr/bin/env python

from __future__ import division
import json
import re

def validate(rcfilename):
    '''Runs several tests over the rich citation JSON contained within the given file.'''

    with open(rcfilename) as f:
        raw = json.load(f)
        t = [a["result"] for a in raw]

    allthere = True
    goodjson = True # innocent until proven guilty
    there = filter(None, t)
    n = len(raw)
    if len(there) != len(t):
        allthere = False
        t = there

    uris = []
    dois = []
    licenses = []
    crossmarks = []
    emptyrefs = 0
    badtitles = []
    try:
        ref_lists = [p["references"] for p in t]
    except KeyError:
        refkeyset = set([u'citation_groups', 
                        u'word_count', 
                        u'references', 
                        u'uri', 
                        u'bibliographic', 
                        u'updated_by'
                        ])
        there = [i for i in t if set(i.keys()) == refkeyset]
        failed = [i for i in t if i.keys() == ["failed"]]
        if len(there) + len(failed) == len(t):
            allthere = False
        else:
            goodjson = False
        t = there
        ref_lists = [p["references"] for p in t]
    finally:
        papers_retrieved = len(there)
    # for paper in t:
    #     refs = paper["references"]
        for refs in ref_lists:
            if len(refs) == 0:
                print "Paper with empty references!"
                emptyrefs += 1
                allthere = False
                papers_retrieved -= 1
            for ref in refs:
                try:
                    uri = ref["uri"]
                    uris.append(uri)
                    try:
                        i = uri.index("dx.doi.org")
                        dois.append(uri)
                        try:
                            title = ref["bibliographic"]["title"]
                        except KeyError:
                            print "Bad JSON found in references!"
                            badtitles.append(ref)
                            # pass
                        else:
                            try:
                                test_title = re.escape(re.sub(r"\W+", "", title)) # Remove non-alphanumerics
                                test_original = re.sub("<.*?>", "", ref["original_citation"]) # remove HTML tags
                                test_original = re.sub(r"\W+", "", test_original) # Remove non-alphanumerics
                                match = re.search(test_title, test_original, re.IGNORECASE) # look for case-insensitive match
                                if not match:
                                    badtitles.append(ref)
                            except KeyError:
                                print "Bad JSON found in references!"
                                badtitles.append(ref)
                                # pass
                    except ValueError:
                        pass
                # for pair in [(uris, ["uri_type"]), (sources, ["uri_source"]), (titles, ['bibliographic', 'title'])]:
                #     l = pair[0]
                #     atts = pair[1]
                #     try:
                #         item = reduce(lambda d, k: d[k], atts, ref) # uses the elements of atts to repeatedly address ref until none are left.
                #         l.append(item)
                except KeyError:
                    uris.append(None)

                try:
                    license = ref["bibliographic"]["license"]
                    licenses.append(license)
                except KeyError:
                    licenses.append(None)
                try:
                    crossmark = ref['updated_by']
                    crossmarks.append(crossmark)
                except KeyError:
                    crossmarks.append(None)




        num_refs = len(uris)
        uri_ratio = len(filter(None, uris))/num_refs
        doi_ratio = len(dois)/num_refs
        if not goodjson:
            return [False, (papers_retrieved, n), (uri_ratio, num_refs, False, licenses, crossmarks, emptyrefs, badtitles), 
                    "Some of the papers retrieved had bad JSON; " + str(len(there)) + " out of " + str(n) + 
                    ''' were successfully retrieved. Of those retrieved: ''' + '\n'
                    + ''' fraction of references with URIs is '''
                    + str(uri_ratio) + ',\n' + 
                    "fraction of references with DOIs is " + str(doi_ratio) + '.\n']
        elif not allthere:
            return [False, (papers_retrieved, n), (uri_ratio, num_refs, True, licenses, crossmarks, emptyrefs, badtitles),
                    "Not all papers requested were retrieved; " + str(len(there)) + " out of " + str(n) + 
                    ''' were successfully retrieved. Of those retrieved:''' + '\n' 
                    + '''fraction of references with URIs is ''' 
                    + str(uri_ratio) + ',\n' + 
                    "fraction of references with DOIs is " + str(doi_ratio) + '.\n']
        else:
            return [True, (n, n), (uri_ratio, num_refs, True, licenses, crossmarks, emptyrefs, badtitles),
                    "Total number of references is " + str(num_refs) + ',\n',
                    "Fraction of references with URIs is " + str(uri_ratio) + ',\n',
                    "Fraction of references with DOIs is " + str(doi_ratio) + '.\n'
                    ]

def multi_validate(rc_prefix, (min, max)):
    '''Runs validation over a range of files, returns total numbers.'''
    total = 0
    processed = 0
    refs = 0
    ratio = 0
    crossmarks = 0
    licenses = 0
    emptyrefs = 0
    badtitles = 0
    for i in range(min, max+1):
        filename = rc_prefix + str(i) + ".json"
        print "Processing " + filename + "..."
        v = validate(filename)
        p = v[1][0]
        t = v[1][1]
        rat = v[2][0]
        ref = v[2][1]
        total += t
        processed += p
        ratio = (ratio*refs + rat*ref)/(refs + ref)
        refs += ref
        if not v[2][2]:
            print "Bad JSON found!"
        licenses += len(filter(None, v[2][3]))
        crossmarks += len(filter(None, v[2][4]))
        emptyrefs += v[2][5]
        badtitles += len(v[2][6])
    return (total, processed, refs, ratio, licenses, crossmarks, emptyrefs, badtitles)

def not_processed(rc_prefix, (min, max)):
    '''Returns a list of DOIs which were not processed for a range of files, returns total numbers.'''
    total = 0
    processed = 0
    notprocessed = []
    for i in range(min, max+1):
        filename = rc_prefix + str(i) + ".json"
        print "Processing " + filename + "..."
        with open(filename) as f:
            raw = json.load(f)
        total += len(raw)
        # missed = [a["doi"] for a in raw if not a["result"]]
        # there = [a for a in raw if a["result"]]
        refkeyset = set([u'citation_groups', 
                u'word_count', 
                u'references', 
                u'uri', 
                u'bibliographic', 
                u'updated_by'
                ])
        there = [a for a in raw if a["result"] and set(a["result"].keys()) == refkeyset and len(a["result"]["references"]) != 0] # boolean short circuit!
        # theredois = {a["doi"] for a in there}
        notthere = [a["doi"] for a in raw if a not in there]
        processed += len(there)
        notprocessed.extend(notthere)
    print processed, "papers processed out of", total, "total;", len(notprocessed), "papers remaining."
    return notprocessed

