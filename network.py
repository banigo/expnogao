#!/usr/bin/env python
# gg
import networkx as nx

G = nx.Graph()
G.add_node("spam")
G.add_edge(1,2)
print(G.nodes())
print(G.edges())
