#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import os
import sys
import json
import networkx as nx
from networkx.readwrite import json_graph
 
###
#pathprefix='/var/www/html/applconn/'
#json_filepath='/usr/local/applconn/applconn.json'
pathprefix='/var/tmp/applconn/'
json_filepath='/var/tmp/applconn/applconn.json'
##

def errorhtml(txt):
    print("Content-Type: text/html")
    print("")
    print("Error: " + txt)
    sys.exit(31)


def drawimage(filename):
    os.system('dot -Tsvg %s/%s.txt -o %s/%s.svg' % (pathprefix, filename, pathprefix, filename))


def main():
    # Initialize Graph
    G=nx.DiGraph()
    with open(json_filepath) as f:
        jsondata=json.loads(f.read())
        G=json_graph.node_link_graph(jsondata)

    ## Write down all the data
    #A=nx.nx_agraph.to_agraph(G)
    #A.write(pathprefix+'a.txt')
    #drawimage('a')
    
    ##
    fs=cgi.FieldStorage()

    if (not fs.has_key('key')):
        errorhtml('No key defined')

    key=fs['key'].value
    if (fs.has_key('reversed')): 
        reversed=True
    else:
        reversed=False
 
    if (not key in G.nodes()):
        errorhtml('No Such key') 

    ## Compute Tree from key node
    if (reversed):
        G=G.reverse()
    st=nx.dfs_tree(G, key)
    
    ### add attribute
    #for node in st.nodes():
    #    node['href']='http://www.google.co.jp'
    
    ## Graphviz
    A=nx.nx_agraph.to_agraph(st)
    A.write('%s/1.txt' % (pathprefix))
    
    ## SVG
    drawimage('1')
    
    ## inline svg
    with open(pathprefix+'/1.svg') as svgfile:
        svgdata=svgfile.read()
    
    ## CGI
    print ("Content-Type: text/html")
    print ("")
    print ("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
                <meta charset="UTF-8">
                <title></title>
        </head>
        <body>
        <h2>graph</h2>
         %s
        <div id="data">
        <a href="../1.txt">データ</a>
        </div>
        </body>
        </html>
        """ % (svgdata)
    )


if __name__ == "__main__":
    main()
