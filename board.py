""" board.py """

from abc import ABCMeta, abstractmethod

from ThreeEventStats import VennGraph

class Statistic(metaclass=ABCMeta):
    @abstractmethod
    def get_graph_stats(self):
        raise NotImplementedError("Create a class that implements")


class IndividualBased(Statistic):
    def __init__(self, graph:VennGraph):
        self.graph = graph
    def get_graph_stats(self):
        print("Individual based")


class ValueBased(Statistic):
    def __init__(self, graph:VennGraph):
        self.graph = graph
    def get_graph_stats(self):
        print("Value based")


class CountBased(Statistic):
    def __init__(self, graph:VennGraph):
        self.graph = graph
    def get_graph_stats(self):
        print("Count based")


"""
 

There's a set S. Want to partition S with some constraints -
We want to partition the set into n parts. There are n non-empty possibly
overlapping subsets that cover S (B0,...,Bn). The i_0...i_nth block has sizes
r_0...r_n and can only use elements x in B_0,...,B_n to make the partition.

Is there a formula I can use/generate to find the number of partitions
that meet this constraint? I know there's the stirling numbers of the
second order, which returns the number of partitions where S of size n
is partitioned into k blocks, but it doesn't have any constraints. I
figure this could be used as an upper bound. I can currently solve
this, but I'm sort of brute forcing it.

"""



def generate_unique_partition_shapes(VennGraph: graph):
    for venn_set, ven_subset in graph.iterate_idk():
        