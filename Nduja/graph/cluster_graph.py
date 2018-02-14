from typing import Dict
from typing import Iterable

from graph_tool.all import *

from graph.cluster import Cluster
from graph.BitcoinTransactionRetriever import BtcTransactionRetriever


class ClusterGraph:

    def __init__(self, cluster_list: Iterable[Cluster]) -> None:
        self._cluster_to_vertex = {}  # type: Dict[Cluster, Vertex]
        self._graph = Graph()

        self._vertex_to_cluster = self._graph.new_vertex_property("object")
        for cluster in cluster_list:
            v = self._graph.add_vertex()
            self._cluster_to_vertex[cluster] = v
            self._vertex_to_cluster[v] = cluster

    def add_vertex(self, cluster: Cluster) -> Vertex:
        """This function take a cluster. Check if it is already present
        a cluster that has some intersection. And if it is the case
        it binds them"""
        present = False
        for k in self._cluster_to_vertex:
            if cluster.intersect(k):
                k.merge(cluster)
                present = True
                v = self._cluster_to_vertex[k]
                break
        if not present:
            cluster.fill_cluster()
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

    def plot(self, output_file_name="/tmp/graphviz.svg", blacklist=[]):
        cluster_size = self._graph.new_vertex_property("int32_t")

        for v in self._graph.vertices():
            cluster = self._vertex_to_cluster[v]
            cluster_size[v] = len(cluster.inferred_addresses)

        graphviz_draw(self._graph,
                      overlap=False,
                      # splines = True
                      elen=1,
                      sep=1,
                      vprops={"width": 4,
                              "height": 4,
                              "fillcolor": "#b7a6ad",
                              "shape": "oval",
                              "label": cluster_size,
                              "fontsize": 100,
                              },
                      eprops={"arrowsize": 7, "color": "black", "penwidth": 7},
                      output=output_file_name,
                      fork=True,
                      gprops={"bgcolor": "white"}
                      # splines=True
                      )
        print("Output written in " + output_file_name)




