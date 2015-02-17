# - Coding UTF8 -
#
# Networked Decision Making
# Site: http://code.google.com/p/global-decision-making-system/
#
# License Code: GPL, General Public License v. 2.0
# License Content: Creative Commons Attribution 3.0
#
# Also visit: www.web2py.com
# or Groups: http://groups.google.com/group/web2py
# 	For details on the web framework used for this development
#
# Developed by Russ King (newglobalstrategy@gmail.com
# Russ also blogs occasionally to pass the time at proudofyourplanent.blogspot.com
# His general thinking on why this project is very important is availalbe at
# http://www.scribd.com/doc/98216626/New-Global-Strategy


try:
    import networkx as nx
    nx_available = True
except ImportError:
    nx_available = False


def getpositions(nodes, links, fixeditem=None):
    if nx_available:
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(links)
        if fixeditem:
            #so this currently doesnt appear to work 
            #the node now seems to fix into centre
            pos = {1:(0,0)}
            fixlist = [1]
            return nx.spring_layout(G, 2, 0.7, pos=pos, fixed=fixlist)
        else:
            return nx.spring_layout(G, 2, 0.7)
    else:
        return dict(bla='bla')
