A collection of utilities and scripts for accessing the PLOS Labs "Rich Citation" API.
Also includes a set of validation scripts and parsing scripts for the JSON that DOIs
are stored in.

apidois.json
    List of the DOIs of the PLOS papers that are loaded into the readwrite API.

api_utilities.py
    Useful functions for accessing the readwrite API 

citation_validation.py  
    Takes the JSON that xml_parsing creates, and makes sure that it did its job correctly.

doi_retrieval_script.py
    Create a list of DOIs from the search_and... script.

search_and_DOI_utilities.py
    Access to the PLOS search API.

xml_parsing.py
    Take a PLOS DOI(s) and put them into the XML ingest engine. Then parse and put into readwrite api

processing_script.py
    Manager script that runs the other scripts in this repository.