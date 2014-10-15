#!/usr/bin/env python

from __future__ import division
import json

def validate(rcfilename):
    '''Runs several tests over the rich citation JSON contained within the given file.'''

    with open(rcfilename) as f:
        raw = json.load(f)
        t = [a["result"] for a in raw]

    # try:
    #     k = [i.keys() for i in t]
    #     a = [j == k[0] for j in k]
    #     if not all(a):
    #         # print "Not all papers requested were retrieved."
    #         # frac = sum(a)/len(a)
    #         return [False, sum(a), len(a), "Not all papers requested were retrieved; " + str(sum(a)) + " out of " + str(len(a)) + " were successfully retrieved."]
    # except AttributeError:
    allthere = True
    there = filter(None, t)
    if len(there) != len(t):
        allthere = False
        n = len(t)
        t = there

    uris = []
    dois = []
    for paper in t:
        refs = paper["references"]
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
    if not allthere:
        return [False, (len(there), n), (uri_ratio, num_refs),
                "Not all papers requested were retrieved; " + str(len(there)) + " out of " + str(n) + " were successfully retrieved."]
    # elif uri_ratio < 0.8:
    #     return [False, uri_ratio, num_refs,
    #             "Total number of references is " + str(num_refs) + '\n',
    #             "Fraction of references with URIs is " + str(uri_ratio) + '\n',
    #             "Fraction of references with DOIs is " + str(doi_ratio) + '\n'
    #             ]
    else:
        return [True, uri_ratio, num_refs,
                "Total number of references is " + str(num_refs) + '\n',
                "Fraction of references with URIs is " + str(uri_ratio) + '\n',
                "Fraction of references with DOIs is " + str(doi_ratio) + '\n'
                ]
