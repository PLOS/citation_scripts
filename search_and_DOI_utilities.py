#!/usr/bin/env python

"""
search_and_DOI_utilities.py
Python utilities for searching for PLOS papers, retrieving them, and obtaining the DOIs cited therein.
External dependencies: beautifulsoup4, lxml, requests
All of these packages can be easilly installed using pip.
"""

from bs4 import BeautifulSoup
from itertools import chain, compress
import requests
from urllib2 import quote
import json
import re
import codecs

def plos_search(query, query_type = None, rows = 20, more_parameters = None, fq = '''doc_type:full AND article_type:"Research Article"''', output = "json", verbose = False):
    '''
    Accesses the PLOS search API.
    query: the text of your query.
    query_type: subject, author, etc.
    rows: maximum number of results to return.
    more_parameters: an optional dictionary; key-value pairs are parameter names and values for the search api.
    fq: determines what kind of results are returned.
    Set by default to return only full documents that are research articles (almost always what you want).
    output: determines output type. Set to JSON by default, XML is also possible, along with a few others.
    '''
    api_key = "s4ZVBmgJyfZPMpqyy3Gs" #for abecker@plos.org

    query_string = ""
    if query_type:
        query_string += query_type + ":"
    query_string += '"' + query + '"'

    params_string = ""
    if more_parameters:
        params_string = "&" + "&".join([key + "=" + quote(value) for key, value in more_parameters.iteritems()])

    fq_string = "&fq=" + quote(fq)

    url = "http://api.plos.org/search?q=" + query_string + params_string + fq_string + "&wt=" + output + "&rows=" + str(rows) + "&api_key=" + api_key
    headers = {'Content-Type': 'application/' + output}
    if verbose:
        print url
    r = requests.get(url, headers=headers)
    r.encoding = "UTF-8" # just to be sure
    return r.json()["response"]["docs"]

def plos_dois(search_results):
    '''Turns search results from plos_search into a list of DOIs.'''
    return [paper["id"] for paper in search_results]

def remote_XML_retrieval(doi, destination = None):
    '''
    Given the DOI of a PLOS paper, downloads the XML and parses it using Beautiful Soup.
    If you'd like to save the XML as a file, set destination to a filename.
    '''
    headers = {"Content-Type":"application/xml"}
    r = requests.get("http://www.plosone.org/article/fetchObjectAttachment.action?uri=info:doi/" + doi + "&representation=XML")
    # Doesn't matter whether it's a PLOS ONE article or not -- this will work for any article in any PLOS journal.
    r.encoding = "UTF-8" # This is needed to keep the encoding on the papers correct.
    if destination:
        f = codecs.open(destination, "w", "utf-8")
        f.write(r.text)
        f.close()
    soup = BeautifulSoup(r.text, features = "xml")
    return soup

def local_XML_parsing(filename):
    '''Opens the given XML file, parses it using Beautiful Soup, and returns the output.'''
    f = codecs.open(filename, "r", "utf-8")
    soup = BeautifulSoup(f, features = "xml")
    f.close()
    return soup

def paper_doi(paper):
    '''Given a soupified PLOS XML paper, returns that paper's DOI.'''
    paper_doi = paper.find("article-id", attrs={"pub-id-type":"doi"}).text
    return paper_doi

def dois_of_references(paper, crossref = False):
    '''
    Returns all the resolvable DOIs for all the references in one paper.
    It searches for a DOI inline, then looks elsewhere if that fails.
    By default, this function looks at the inline HTML DOIs on the PLOS website for the DOIs if they can't be found inline.
    If crossref=True, it uses CrossRef instead.
    CrossRef is generally slower, which is why crossref = False by default.
    '''
    # Get the doi of the given paper.
    paper_doi = plos_paper_doi(paper)
    # Find all the references.
    references = paper.find_all("ref")
    max_ref_num = len(references)
    ref_nums = range(1, max_ref_num + 1)
    refs = {i:r.text for i, r in zip(ref_nums, references)}
    dois = {}
    cr_queries = {}
    # Try searching for inline DOIs first.
    for i, ref in refs.iteritems():
        doimatch = re.search(r"\sdoi:|\sDOI:|\sDoi:|\.doi\.|\.DOI\.", ref)
        if doimatch:
            rawdoi = ref[doimatch.start():]
            try:
                doi = rawdoi[rawdoi.index("10."):]
                # all DOI's start with 10., see reference here: http://www.doi.org/doi_handbook/2_Numbering.html#2.2
            except ValueError:
                # if a ValueError is raised, that means the DOI doesn't contain the string '10.' -- which means it's not a valid DOI.
                cr_queries[i] = ref
                continue # jump to the next reference

            # Removing whitespace and anything afterwards.
            space = re.search(r"\s", doi)
            if space:
                doi = doi[:space.start()]

            # Removing trailing periods.
            if doi[-1] == ".":
                doi = doi[:-1]

            dois[i] = doi
        else:
            cr_queries[i] = ref

    if crossref:
        # Now search for the DOIs on Crossref.
        url = "http://search.crossref.org/links"
        data = json.dumps(cr_queries.values())
        headers = {"Content-Type":"application/json"}
        r = requests.post(url, data = data, headers = headers)
        if r.json()["query_ok"]:
            results = r.json()["results"]
        else:
            print "There's a problem with the CrossRef DOI search. Check your internet connection and confirm the original paper was properly formatted in the PLOS XML style, then try again."
            return None

        for i, result in zip(cr_queries.keys(), results):
            if result["match"]:
                rawdoi = result["doi"]
                doi = rawdoi[rawdoi.index("10"):] # CrossRef returns DOIs of the form http://dx.doi/org/10.<whatever>
                dois[i] = doi
            else:
                dois[i] = None
    else:
        paper_url = "http://www.plosone.org/article/info:doi/" + paper_doi
        paper_request = requests.get(paper_url)
        paper_html = BeautifulSoup(paper_request.content)
        html_reflist = paper_html.find(attrs={"class":"references"})
        refnums = html_reflist.findChildren("span", attrs={"class":"label"})
        html_references = [r.next_sibling.next_sibling for r in refnums]
        for i in cr_queries.iterkeys():
            ref = html_references[i-1]
            doimatch = re.search(r"\sdoi:|\sDOI:|\sDoi:|\.doi\.|\.DOI\.", ref)
            if doimatch:
                rawdoi = ref[doimatch.start():]
                try:
                    doi = rawdoi[rawdoi.index("10."):]
                    # all DOI's start with 10., see reference here: http://www.doi.org/doi_handbook/2_Numbering.html#2.2
                except ValueError:
                    # if a ValueError is raised, that means the DOI doesn't contain the string '10.' -- which means it's not a valid DOI.
                    dois[i] = None
                    continue # jump to the next reference

                # Removing whitespace and anything afterwards.
                space = re.search(r"\s", doi)
                if space:
                    doi = doi[:space.start()]

                # Removing trailing periods.
                if doi[-1] == ".":
                    doi = doi[:-1]

                dois[i] = doi
            else:
                dois[i] = None
    return dois


# Example usage:
#
# SEARCH_SUBJECT = "circadian rhythms"
# MAX_PAPERS = 500
# search_results = plos_search(SEARCH_SUBJECT, query_type = "subject", rows = MAX_PAPERS)
# print "Retrieving " + str(len(search_results)) + " papers from PLOS journals..."
# dois = plos_dois(search_results)
# papers = [remote_XML_retrieval(doi) for doi in dois]
# first_paper = paper[0]
# cited_dois = dois_of_references(first_paper)
