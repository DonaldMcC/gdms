# From python algorithms Listing 5-4
# so this requires to be an adjacency list

from builtins import range
def rec_dfs(G, s, S=None):
    """ 
    >>> rec_dfs([[1,2,3,4,5],[1,5],[],[],[5],[]],0)
    set([0, 1, 2, 3, 4, 5])

    """

    if S is None:
        S = set()  # Initialize history
    S.add(s)  # visited s

    for u in G[s]:
        if u in S:
            continue
        rec_dfs(G, u, S)
    return S


def iter_dfs(G, s):
    """ 
    >>> list(iter_dfs([[1,2,3,4,5],[1,5],[],[],[5],[]],0))
    [0, 1, 5, 2, 3, 4]
    
    >>> list(iter_dfs([[1, 2, 3, 4, 5], [3], [], [5], [5], []],0))
    [0, 1, 3, 5, 2, 4]
    """
    S, Q = set(), []  # Visited set and queue

    Q.append(s)
    while Q:
        u = Q.pop()
        if u in S:
            continue
        S.add(u)
        G[u].reverse()
        Q.extend(G[u])
        yield u

        
def get_trav_list(nodes, indices):
    """ 
    >>> get_trav_list([0, 2, 5, 15, 3, 4],[0, 1, 5, 2, 3, 4])
    [0, 2, 4, 5, 15, 3]
    """
    return [nodes[x] for x in indices]

    
def conv_for_iter(nodes, edges):
    """ 

    >>> conv_for_iter([2,5,15,3,4],[(2,15),(15,4),(3,4)])
    [[1, 2, 3, 4, 5], [3], [], [5], [5], []]
    
    so idea is that nodes are sorted in order of position from top left
    and the event is basically an invisible node which also has links to all edges so
    we prepend node 0 and then do full iteration to build the graph but then ignore 0
    at end of the process as well - that way we do have a full directed graph
    """
    G = [[] for x in range(len(nodes)+1)]
    G[0] = range(1,len(nodes)+1)  # connect 0 to all nodes in event order
    nodes.insert(0, 0)  # add 0 to nodes b

    for x in edges:
        position = nodes.index(x[0])
        G[position].append(nodes.index(x[1]))
        
    return G
    

def _test():
    import doctest
    doctest.testmod()
    
if __name__ == '__main__':
    # Can run with -v option if you want to confirm tests were run
    _test()   