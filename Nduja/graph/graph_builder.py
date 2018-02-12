from math import log
from math import sqrt
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from graph_tool.all import *
from graph_tool.all import Edge
from graph_tool.all import Vertex
from graph_tool.all import PropertyMap


class CurrencyGraph:
    """This class represent the transition graph for a single currency"""

    def __init__(self, list_of_addresses: List[str]) -> None:
        self.G = Graph()
        self.vertex_name_property = self.G.new_vertex_property("string")
        self.edge_ivalue_property = self.G.new_edge_property("vector<int64_t>")
        self.edge_ovalue_property = self.G.new_edge_property("vector<int64_t>")
        self.edge_weight_property = self.G.new_edge_property("int32_t")
        self.edge_transaction_property = \
            self.G.new_edge_property("vector<string>")
        # This dictionary stores the inverse mapping of vertex_name_property
        self.vertex_name_to_vertex_index = {}  # type: Dict[str, int]
        self.original_nodes = []  # type: List[int]

        for address in list_of_addresses:
            v_index = self.G.add_vertex()
            self.vertex_name_property[v_index] = address
            self.vertex_name_to_vertex_index[address] = v_index
            self.original_nodes.append(v_index)

        self.original_nodes_names_list = list_of_addresses

    def get_original_nodes(self) -> List[str]:
        return self.original_nodes_names_list

    def get_edge(self, u: int, v: int) -> Optional[Edge]:
        edge = None
        try:
            edge = self.G.edge(u, v)
        except ValueError:
            pass
        return edge

    def get_node(self, address: str) -> Optional[int]:
        v_index = None
        try:
            v_index = self.vertex_name_to_vertex_index[address]
        except KeyError:
            pass
        return v_index

    def add_str_edge(self, u: str, v: str, **kwargs: Dict[str, Any]) -> bool:
        u_vertex = self.vertex_name_to_vertex_index[u]
        v_vertex = self.vertex_name_to_vertex_index[v]

        e = self.get_edge(u_vertex,
                          v_vertex
                          )

        if e is None:
            e = self.G.add_edge(u_vertex, v_vertex)
            self.edge_weight_property[e] = kwargs["weight"]
        else:
            self.edge_weight_property[e] += kwargs["weight"]
        return True

    def add_edge(self, u: Vertex, v: Vertex, **kargs: Dict[str, Any]) -> Edge:
        """Add an edge from u to v containing the number of transactions
        from u to v. Return the Edge instance"""
        t = kargs["trx"]
        ivalue = kargs["ivalue"]
        ovalue = kargs["ovalue"]

        u_index = self.add_node(u)
        v_index = self.add_node(v)

        e = self.get_edge(u_index,
                          v_index
                          )

        if e is None:

            e = self.G.add_edge(u_index, v_index)
            self.edge_transaction_property[e] = [t]
            self.edge_ivalue_property[e].append(ivalue)
            self.edge_ovalue_property[e].append(ovalue)
            self.edge_weight_property[e] = 1

        else:

            # The transaction was already added
            if t not in self.edge_transaction_property[e]:
                self.edge_weight_property[e] += 1
                self.edge_ivalue_property[e].append(ivalue)
                self.edge_ovalue_property[e].append(ovalue)
                self.edge_transaction_property[e].append(t)
        return e

    def add_node(self, address: str) -> Vertex:
        """Add a node to the multidigraph"""
        v_index = self.get_node(address)
        if v_index is None:
            v_index = self.G.add_vertex()
            self.vertex_name_property[v_index] = address
            self.vertex_name_to_vertex_index[address] = v_index
        return v_index

    def connected_components_non_trivial(self, blacklist=[]) -> PropertyMap:
        c = label_components(self.G, directed=False)
        components = c[0]
        hist = c[1]
        # PropertyMap containing all vertices in a component with more than two
        # vertices and the vertex is in the initial list
        vfilt = self.G.new_vertex_property('bool')

        for i in range(len(list(components.a))):
            if hist[components.a[i]] > 1:
                vfilt[i] = True
            elif self.vertex_name_property[i] in self.original_nodes_names_list\
                    and not self.vertex_name_property[i] in blacklist:
                vfilt[i] = True
            else:
                vfilt[i] = False
        return vfilt

    def plot(self, output_file_name="/tmp/graphviz.svg", blacklist=[]):
        vfilt = self.connected_components_non_trivial(blacklist)

        gv = GraphView(self.G, vfilt=vfilt)

        graphviz_draw(gv,
                      overlap=False,
                      # splines = True
                      elen=1,
                      sep=1,
                      vprops={"width": 4,
                              "height": 4,
                              "fillcolor": "red",
                              "shape": "oval"},
                      eprops={"arrowsize": 7, "color": "black", "penwidth": 7},
                      output=output_file_name,
                      fork=True,
                      gprops={"bgcolor": "white"}
                      # splines=True
                      )
        print("Output written in " + output_file_name)














