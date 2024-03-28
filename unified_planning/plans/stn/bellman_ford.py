# Python3 program for Bellman-Ford's single source
# shortest path algorithm.

# Class to represent a graph

class Graph:

    def __init__(self, vertices):
        self.V = vertices  # list of vertices
        self.graph = []

    # function to add an edge to graph
    def addEdge(self, u, v, w):
        self.graph.append([u, v, w])

    # utility function used to print the solution
    def printArr(self, dist):
        print("Vertex Distance from Source")
        for i in self.V:
            print("{0}\t\t{1}".format(i, dist[i]))

    # The main function that finds shortest distances from src to
    # all other vertices using Bellman-Ford algorithm. The function
    # also detects negative weight cycle
    def BellmanFord(self, src):

        # Step 1: Initialize distances from src to all other vertices
        # as INFINITE
        dist = {i: float("Inf") for i in self.V}
        dist[src] = 0

        # Step 2: Relax all edges |V| - 1 times. A simple shortest
        # path from src to any other vertex can have at-most |V| - 1
        # edges
        for _ in range(len(self.V) - 1):
            # Update dist value and parent index of the adjacent vertices of
            # the picked vertex. Consider only those vertices which are still in
            # queue
            for u, v, w in self.graph:
                if dist[u] != float("Inf") and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w

        # Step 3: check for negative-weight cycles. The above step
        # guarantees shortest distances if graph doesn't contain
        # negative weight cycle. If we get a shorter path, then there
        # is a cycle.

        for u, v, w in self.graph:
            if dist[u] != float("Inf") and dist[u] + w < dist[v]:
                print("Graph contains negative weight cycle")
                return

        return dist



# Driver's code
if __name__ == '__main__':
    g = Graph(['start','a', 'b','end'])
    g.addEdge('start', 'end', 6)
    g.addEdge('a', 'start', 0)
    g.addEdge('b', 'a', -5)
    g.addEdge('a', 'b', 5)
    g.addEdge('end', 'a', 0)
    g.addEdge('end', 'b', 0)


    # function call
    g.BellmanFord('start')