import api_utilities
import networkx as nx
import matplotlib.pyplot as plt


def make_group_tree(identifier,idtype='doi',level=0,maxlevel=2):
    '''Returns a networkX graph based on papers available in the database.

    Give a doi, or a uri if the keyword argument idtype = 'uri'

    Example:
    -------
    import citationTrees
    import api_utilities
    import networkx as nx
    import matplotlib.pyplot as plt
    
    doi = api_utilities.randdoi()
    G =  citationTrees.make_group_tree(doi)  # Use this script to make the network
    nx.draw(G,node_color=[G.node[node]['color'] for node in G]) # Draw the map; colors are included as node property
    plt.show()  # Need to run if not using interactive matplotlib
    '''

    G = nx.Graph()
    G.add_node(identifier,color='blue')

    if idtype=='doi':
        if not api_utilities.in_database(identifier):
            return G #no more to add to graph
        else:
            d =  api_utilities.citations(identifier)
    else:
        if not api_utilities.in_database_from_uri(identifier):
            return G #no more to add to graph
        else:
            d =api_utilities.citations_from_uri(identifier)

    try:
        d['citation_groups'] #check if this key exists
    except KeyError:
        return G 

    for grp in d['citation_groups']:
        G.add_node((identifier, grp['id']),text_before=grp['context']['text_before'],text_after=grp['context']['text_after'],color='red')
        G.add_edge(identifier,(identifier, grp['id']),label=grp['id'])

    for ref in d['references']:
        G.add_node(ref['uri'],color='blue')
        for i in ref['citation_groups']:
            G.add_edge(ref['uri'],(identifier,i))
     
    # ADDING MORE LEVELS
    if level!=maxlevel:
        for ref in d['references']:
            if len(ref['citation_groups']) >= 2:
                uri = ref['uri']
                newG = make_group_tree(uri,idtype='uri',level=level+1,maxlevel=maxlevel)
                G=nx.compose(G,newG)
        
    return G



