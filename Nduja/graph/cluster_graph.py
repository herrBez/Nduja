from typing import Dict, List
from typing import Iterable

from graph_tool.all import *

from graph.cluster import Cluster
from graph.bitcoin_transaction_retriever import BtcTransactionRetriever


class ClusterGraph:

    def __init__(self, cluster_list,
                 black_list_cluster):
        self._cluster_to_vertex = {}  # type: Dict[Cluster, Vertex]
        self._graph = Graph()

        self._vertex_to_cluster = \
            self._graph.new_vertex_property("object")  # type: ignore

        for cluster in cluster_list:
            v = self._graph.add_vertex()
            self._cluster_to_vertex[cluster] = v
            self._vertex_to_cluster[v] = cluster
        self.black_list_cluster = black_list_cluster
        v = self._graph.add_vertex()
        self._cluster_to_vertex[black_list_cluster] = v
        self._vertex_to_cluster[v] = black_list_cluster

    def add_vertex(self, cluster: Cluster):
        """This function take a cluster. Check if it is already present
        a cluster that has some intersection. And if it is the case
        it binds them"""
        present = False
        cluster.fill_cluster(self.black_list_cluster)

        for k in self._cluster_to_vertex:
            if cluster.intersect(k):
                k.merge(cluster)
                present = True
                v = self._cluster_to_vertex[k]
                break
        if not present:
            print("cluster_graph: cluster : begin" + str(cluster.original_addresses.copy().pop()))
            print("cluster_graph: cluster : end")
            v = self._graph.add_vertex()
            self._cluster_to_vertex[cluster] = v
            self._vertex_to_cluster[v] = cluster
        return v

    def add_edge(self, cluster_from: Cluster, cluster_to: Cluster):
        """This function add two edges. If the """
        vertex_from = self.add_vertex(cluster_from)
        vertex_to = self.add_vertex(cluster_to)

        if self._graph.edge(vertex_from, vertex_to) is None:
            self._graph.add_edge(vertex_from, vertex_to)

    def plot(self, output_file_name="/tmp/graphviz.svg"):
        print("Plotting")

        cluster_label = self._graph.new_vertex_property("string")

        for v in self._graph.vertices():
            cluster = self._vertex_to_cluster[v]
            cluster_label[v] = str(list(cluster.ids)[0]) + \
                               "|" + \
                               str(len(cluster.inferred_addresses))


        graphviz_draw(self._graph,
                      overlap=False,
                      # splines = True
                      elen=1,
                      sep=1,
                      vprops={"width": 4,
                              "height": 4,
                              "fillcolor": "#b7a6ad",
                              "shape": "oval",
                              "label": cluster_label,
                              "fontsize": 100,
                              },
                      eprops={"arrowsize": 7, "color": "black", "penwidth": 7},
                      output=output_file_name,
                      fork=True,
                      gprops={"bgcolor": "white"}
                      # splines=True
                      )
        print("Output written in " + output_file_name)




