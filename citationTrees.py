import api_utilities
import networkx as nx
import matplotlib.pyplot as plt


def make_group_tree(identifier,idtype='doi'):
    '''Returns a networkX graph based on papers available in the database.

    Give a doi, or a uri if idtype is set to 'uri'
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

    for grp in d['citation_groups']:
        G.add_node((identifier, grp['id']),text_before=grp['context']['text_before'],text_after=grp['context']['text_after'],color='red')

        G.add_edge(identifier,(identifier, grp['id']))

    for ref in d['references']:
        G.add_node(ref['uri'],color='blue')
        for i in ref['citation_groups']:
            G.add_edge(ref['uri'],(identifier,i))
        
    return G


# Example:
#doi = api_utilities.randdoi()
#G =  make_group_tree(doi)
#nx.draw(G,node_color=[G.node[node]['color'] for node in G])
#plt.show()

