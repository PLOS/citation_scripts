#!/usr/bin/env python

from __future__ import division
import json

def validate(rcfilename):
    '''Runs several tests over the rich citation JSON contained within the given file.'''

    with open(rcfilename) as f:
        raw = json.load(f)
        t = [a["result"] for a in raw]

    allthere = True
    goodjson = True # innocent until proven guilty
    there = filter(None, t)
    n = len(t)
    if len(there) != len(t):
        allthere = False
        t = there

    uris = []
    dois = []
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
    # for paper in t:
    #     refs = paper["references"]
        for refs in ref_lists:
            for ref in refs:
                try:
                    uri = ref["uri"]
                    uris.append(uri)
                    try:
                        i = uri.index("dx.doi.org")
                        dois.append(uri)
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

        num_refs = len(uris)
        uri_ratio = len(filter(None, uris))/num_refs
        doi_ratio = len(dois)/num_refs
        if not goodjson:
            return [False, (len(there), n), (uri_ratio, num_refs, False), 
                    "Some of the papers retrieved had bad JSON; " + str(len(there)) + " out of " + str(n) + 
                    ''' were successfully retrieved. Of those retrieved: fraction of references with URIs is '''
                    + str(uri_ratio) + ',\n' + 
                    "fraction of references with DOIs is " + str(doi_ratio) + '.\n']
        elif not allthere:
            return [False, (len(there), n), (uri_ratio, num_refs),
                    "Not all papers requested were retrieved; " + str(len(there)) + " out of " + str(n) + 
                    ''' were successfully retrieved. Of those retrieved: fraction of references with URIs is ''' 
                    + str(uri_ratio) + ',\n' + 
                    "fraction of references with DOIs is " + str(doi_ratio) + '.\n']
        else:
            return [True, uri_ratio, num_refs,
                    "Total number of references is " + str(num_refs) + ',\n',
                    "Fraction of references with URIs is " + str(uri_ratio) + ',\n',
                    "Fraction of references with DOIs is " + str(doi_ratio) + '.\n'
                    ]