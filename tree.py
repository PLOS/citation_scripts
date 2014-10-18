import api_utilities
import networkx as nx
import matplotlib.pyplot as plt

'''class CitationTree:
    def __init__(self,doi,levels=3):

        if not api_utilities.in_database(doi):
            pass

        else:
            self.root=api_utilities.citations(doi)['uri']

            self.G=nx.Graph()
            self.Gall.add_node(self.root)

            self.make_tree(self.root,maxlevel=levels)

    def draw(self):
        nx.draw(self.G)
        plt.show()


    def make_tree_all(self,node0,level=0,maxlevel=3):
        if not api_utilities.in_database_from_uri(node0):
            return None

        try:
            for paper in api_utilities.citations_from_uri(node0)['references']:
                node = paper['uri']
                self.G.add_node(node)
                self.G.add_edge(node0,node)
            
                # if current level is less than maxlevel, 
                # add subtree for this paper
                if level==maxlevel:
                    pass
                else:
                    self.make_tree(node,level=level+1)

            return None
                    
        except KeyError:
            # no references in the database
            return None'''



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


#nx.draw(p,node_color=[p.node[node]['color'] for node in p])
#plt.show()

