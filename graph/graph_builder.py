import networkx as nx
import matplotlib.pyplot as plt


class CurrencyGraph:
    """This class represent the transition graph for a single currency"""

    def __init__(self, list_of_addresses):
        self.MG = nx.MultiDiGraph()
        self.MG.add_nodes_from(list_of_addresses)
        self.original_nodes = list_of_addresses

    def add_edge(self, u, v, transactions):
        """Add an edge from u to v containing the number of transactions
        from u to v"""
        self.MG.add_edge(u, v, transactions=transactions)

    def add_node(self, u):
        """Add a node to the multidigraph"""
        self.MG.add_node(u)


    def plot_multigraph(self):
        node_colours = ["red" if node in self.original_nodes else "black"
                        for node in self.MG.nodes]


        nx.draw(self.MG,
                pos=nx.circular_layout(self.MG),
                alpha=0.5,
                node_color=node_colours,
                )
        nx.draw_networkx_edge_labels(self.MG, pos=nx.circular_layout(self.MG))
        plt.show()


    # @abstractmethod
    # def get_connected_component_for_node(self, node):
    #     """This function should return the subgraph for a specific node"""
    #
    #     pass


    pass


g = CurrencyGraph([1, 2, 3])
g.add_edge(4,5,10)
g.add_edge(1,3,11)
g.add_edge(4,1,12)
g.plot_multigraph()


