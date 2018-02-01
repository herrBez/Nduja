import networkx as nx
import matplotlib.pyplot as plt
import logging

class CurrencyGraph:
    """This class represent the transition graph for a single currency"""

    def __init__(self, list_of_addresses):
        self.MG = nx.MultiDiGraph()
        self.MG.add_nodes_from(list_of_addresses)
        self.original_nodes = list_of_addresses

    def add_edge(self, u, v, transactions):
        """Add an edge from u to v containing the number of transactions
        from u to v"""
        self.MG.add_edge(u, v, t=transactions)

    def add_node(self, u):
        """Add a node to the multidigraph"""
        self.MG.add_node(u)


    def plot_multigraph(self, node = None):
        """Plot the multigraph marking the original nodes with red and the new
        ones with black. If a node is provided. It plots only the weak component
        containing the given node"""
        G = self.MG
        if node is not None:
            G = self.get_connected_component_for_node(node)

        node_colours = ["red" if node in self.original_nodes else "blue"
                        for node in G.nodes]

        # edge_list = G.edges

        max_val = 1
        for e in G.edges(data=True):
            print(e[2]["t"])
            max_val = max(e[2]["t"], max_val)

        # line_widths = [(e[2]["t"]/max_val)*3 for e in G.edges(data=True)]

        pos = nx.circular_layout(G)
        nx.draw(G,
                pos,
                node_color=node_colours,
                alpha=0.9,
                with_labels=True,
                widths=2
                )

        edge_labels = dict([((u, v,), d['t'])
                            for u, v, d in G.edges(data=True)])

        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                     label_pos=0.2, font_size=7)

        plt.show()

    def get_connected_component_for_node(self, node):
        """This function should return the subgraph for a specific node"""
        if node not in list(self.MG.nodes):
            logging.warning("The given node is not contained in the graph")
            ret = nx.MultiDiGraph()
        else:
            wcc = nx.weakly_connected_component_subgraphs(self.MG)

            for w in wcc:
                if node in list(w.nodes):
                    ret = w
                    break
        return ret

    pass


g = CurrencyGraph([1, 2, 3])
g.add_edge(4, 5, 10)
g.add_edge(5, 4, 4)
g.add_edge(4, 1, 5)

# g.plot_multigraph(2)
g.plot_multigraph(4)


