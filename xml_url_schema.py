#!/usr/bin/env python
# coding=utf-8

import json
from urlparse import urlparse
import requests

'''
xml_url_schema.py

Utilities to go from DOI to the URL for the XML of the paper.
Right now, this works for papers published by PLOS, PeerJ, eLife, and all OA content from Springer (including BMC).
Next up: PMC and Bioline International
'''


publisher_xml_url_schema = {
"PeerJ":{"use_doi":False, "tail":".xml"},
"eLife Sciences Publications, Ltd.":{"use_doi":False, "tail":".source.xml"},
"Springer Science + Business Media": {"use_doi":True, "use_doi_prefix":False, "path_head":"/content/download/xml/", "path_tail":".xml"},
"Public Library of Science (PLoS)": {"use_doi":True, "use_doi_prefix":True, "path_head":"/article/fetchObjectAttachment.action?uri=info:doi/", "path_tail":"&representation=XML"}
}

def doi_content_negotiation(doi):
    '''
    Returns citation info in citeproc format.
    See http://www.crosscite.org/cn/ for more info.
    Only accepts raw DOIs as input.
    '''
    url = "http://dx.doi.org/" + doi
    headers = {"Accept":"application/vnd.citationstyles.csl+json"}
    response = requests.get(url, headers=headers)
    parsed = json.loads(response.text)
    return parsed

def doi_to_publisher(doi):
    "Does what it says on the tin."
    cn = doi_content_negotiation(doi)
    try:
        return cn["publisher"]
    except KeyError:
        return False

def doi_to_journal(doi):
    "Does what it says on the tin."
    cn = doi_content_negotiation(doi)
    try:
        return cn["container-title"]
    except KeyError:
        try:
            return cn["journal"]
        except KeyError:
            return False


def doi_to_xml_url(doi):
    "Does what it says on the tin."
    publisher = doi_to_publisher(doi)
    # journal = doi_to_journal(doi)
    schema = publisher_xml_url_schema[publisher]
    r = requests.get("http://dx.doi.org/" + doi)
    url = r.url
    if schema["use_doi"]:
        i = doi.index("/")
        suffix = doi[i+1:]
        prefix = doi[:i]
        parsedurl = urlparse(url)
        if schema["use_doi_prefix"]:
            xml_url = "http://" + parsedurl.netloc + schema["path_head"] + doi + schema["path_tail"]
        else:
            xml_url = "http://" + parsedurl.netloc + schema["path_head"] + suffix + schema["path_tail"]
    else:
        if url[-1] == "/":
            url = url[:-1]
        xml_url = url + schema["tail"]
    return xml_url
