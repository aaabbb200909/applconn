#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import os
import sys
import json
import urllib
import networkx as nx
from networkx.readwrite import json_graph
 
###
enable_ganglia=True
ganglia_url='http://172.17.0.2/ganglia/'
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
    for n in st:
     tmp = st.node[n]
     tmp['name'] = n
     if (enable_ganglia):
      metric_url='{0}/api/metrics.php?host={1}&metric_name=load_one'.format(ganglia_url, n)
      f = urllib.urlopen(metric_url)
      js=json.loads(f.read()) # {"status":"ok","message":{"metric_value":"0.51","units":" "}}
      f.close()

      load_one=float(js['message']['metric_value'])
      if (1.0 < load_one):
       tmp['color'] = '#ff634f'
      elif (0.5 < load_one < 1.0):
       tmp['color'] = '#ffde5e'
      else:
       tmp['color'] = '#e2ecff'
      #raise Exception, tmp['color']
      tmp['href'] = '{0}?c=unspecified&h={1}'.format(ganglia_url, n)
     else: 
      if (G.node[n].has_key('color')):
       tmp['color'] = G.node[n]['color']
      if (G.node[n].has_key('href')):
       tmp['href'] = G.node[n]['href']

    # json output
    js=json_graph.node_link_data(st)
    with open('{0}/1.json'.format(pathprefix), 'w') as f:
        f.write(json.dumps(js, sort_keys=True, indent=4))
    
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
        <div id="d3">

    <div id="chart"></div>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.4.11/d3.min.js"></script>
    <link type="text/css" rel="stylesheet" href="../applconn.css"/>
    <script>var jsonpath="../1.json";</script>
    <script type="text/javascript" src="../applconn.js"></script>

        <a href="../1.json">d3-graph-data</a>
        </div>
        </body>
        </html>
        """ % (svgdata)
    )


if __name__ == "__main__":
    main()
