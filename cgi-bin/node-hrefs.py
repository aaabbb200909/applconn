#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import os
import sys
import json
import networkx as nx
from networkx.readwrite import json_graph
 
###
enable_ganglia=True
ganglia_url='http://127.0.0.1/ganglia/'
kibana_url='http://172.17.0.5:5601/app/kibana#/doc/*/applconn/'
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


def main():
    # Initialize Graph
    G=nx.DiGraph()
    with open(json_filepath) as f:
        jsondata=json.loads(f.read())
        G=json_graph.node_link_graph(jsondata)

    ##
    fs=cgi.FieldStorage()

    if (not fs.has_key('key')):
     errorhtml('No key defined')
    key=fs['key'].value
    if (not key in G.nodes()):
     errorhtml('No Such key') 

    # create urls:
    urls = []


    # default url
    if (G.node[key].has_key('href')):
     urls.append(G.node[key]['href'])
    # ganglia url
    urls.append('{0}?c=unspecified&h={1}'.format(ganglia_url, key))
    # kibana url
    urls.append('{0}{1}?id={2}'.format(kibana_url, key, G.node[key]['kibanaid']))

    # join urls
    urlhtml='<br/>'.join(
     '<a href="{0}">link</a>'.format(url) for url in urls
    )

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
         {0}
        </body>
        </html>
        """.format (urlhtml)
    )


if __name__ == "__main__":
    main()
