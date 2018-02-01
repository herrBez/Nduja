import networkx as nx
import matplotlib.pyplot as plt
import logging


class CurrencyGraph:
    """This class represent the transition graph for a single currency"""

    def __init__(self, list_of_addresses):
        self.G = nx.DiGraph()
        self.G.add_nodes_from(list_of_addresses)
        self.original_nodes = list_of_addresses

    def get_original_nodes(self):
        return self.original_nodes

    def add_edge(self, u, v, **kargs):
        """Add an edge from u to v containing the number of transactions
        from u to v"""
        t = kargs["trx"]
        ivalue = kargs["ivalue"]
        ovalue = kargs["ovalue"]

        if not self.G.has_edge(u, v):
            self.G.add_edge(u, v,
                            w=1,
                            trxs=[t],
                            ivalues=[ivalue],
                            ovalues=[ovalue]
                            )
            print(self.G.edges(data=True))
        else:
            d = self.G.get_edge_data(u, v)
            transactions = d["trxs"]
            # if t in trxs it is already present in the graph
            if t not in transactions:
                w = d["w"]
                ivalues_list = d["ivalues"]
                ivalues_list.append(ivalue)
                ovalues_list = d["ovalues"]
                ovalues_list.append(ovalue)
                transactions.append(t)
                self.G.add_edge(u, v, w=(w + 1),
                                trxs=transactions,
                                ivalues=[ivalues_list],
                                ovalues=[ovalues_list])

    def add_node(self, u):
        """Add a node to the multidigraph"""
        self.G.add_node(u)


    def plot_multigraph(self, node = None):
        """Plot the multigraph marking the original nodes with red and the new
        ones with black. If a node is provided. It plots only the weak component
        containing the given node"""
        g = self.G
        if node is not None:
            g = self.get_connected_component_for_node(node)

        node_colours = ["red" if node in self.original_nodes else "blue"
                        for node in g.nodes]


        shells = [
            [n for n in g.nodes if n in self.original_nodes],
            [n for n in g.nodes if n not in self.original_nodes]
            ]

        node_size = [200 if n in self.original_nodes else 100 for n in g.nodes]

        pos = nx.shell_layout(g, shells)
        nx.draw(g,
                pos,
                node_color=node_colours,
                alpha=1.0,
                # with_labels=True,
                widths=2,
                node_size=node_size,
                linewidths=0.7
                )

        edge_labels = dict([((u, v), d['w'])
                            for u, v, d in g.edges(data=True)])

        nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels,
                                     label_pos=0.3, font_size=7)

        plt.show()

    def get_connected_component_for_node(self, node):
        """This function should return the subgraph for a specific node"""
        if node not in list(self.G.nodes):
            logging.warning("The given node is not contained in the graph")
            ret = nx.DiGraph()
        else:
            wcc = nx.weakly_connected_component_subgraphs(self.G)

            for w in wcc:
                if node in list(w.nodes):
                    ret = w
                    break
        return ret

    pass


# g = CurrencyGraph([1, 2, 3])
# g.add_edge(4, 5, 10)
# g.add_edge(5, 4, 4)
# g.add_edge(4, 1, 5)
#
# # g.plot_multigraph(2)
# g.plot_multigraph(4)


