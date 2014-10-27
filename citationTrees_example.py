import citationTrees
import api_utilities
import networkx as nx
import matplotlib.pyplot as plt


if __name__=='__main__':
    doi = api_utilities.randdoi()
    G =  citationTrees.make_group_tree(doi)  # makes the network
    pos=nx.spring_layout(G)
    nx.draw(G,pos,node_color=[G.node[node]['color'] for node in G]) # Draw the map; colors are included as node property

    labels = {} #create label dictionary; grab from node properties
    for node in G:
        if G.node[node]['color']=='red':
            labels[node] = ''
        else:
            labels[node] = G.node[node]['label']
    nx.draw_networkx_labels(G, pos, labels)

    plt.show()  # if not using interactive matplotlib
