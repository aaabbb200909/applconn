#!/usr/bin/python
import cgi
import os
import sys
import json
import urllib
import networkx as nx
from networkx.readwrite import json_graph
from flask import Flask, render_template, url_for, request, redirect
import settings

app = Flask(__name__)

enable_ganglia=settings.enable_ganglia
ganglia_url=settings.ganglia_url
kibana_url=settings.kibana_url
pathprefix=settings.pathprefix
json_filepath=settings.json_filepath

def errorhtml(txt):
    return ("Error: " + txt)

def drawimage(filename):
    os.system('dot -Tsvg %s/%s.txt -o %s/%s.svg' % (pathprefix, filename, pathprefix, filename))


@app.route("/applconn", methods=["POST"])
def applconn():
    # Initialize Graph
    G=nx.DiGraph()
    with open(json_filepath) as f:
        jsondata=json.loads(f.read())
        G=json_graph.node_link_graph(jsondata)

    fs=request.form

    if (not fs.has_key('key')):
        errorhtml('No key defined')
    key=fs['key']
    if (not key in G.nodes()):
        errorhtml('No Such key') 

    compute_mode="dfs" # "dfs", "distance"
    if fs.has_key("dfsmode"):
     compute_mode="dfs"
    elif fs.has_key("distancemode"):
     compute_mode="distance"
     if (fs.has_key('distance')): 
      distance=fs['distance']
     else:
      distance=None # infinite large number
     if (fs.has_key('graphtype')): 
      graphtype=fs['graphtype'] # 'undirectional' or 'directional'
     else:
      graphtype='directional'
    elif fs.has_key("shortestpathmode"):
     compute_mode="shortestpath"
     if (fs.has_key('shortest_path_target')):
      shortest_path_target=fs['shortest_path_target']
     else:
      errorhtml("No shortest_path_target is given")
    else:
     errorhtml("No computation mode is specified")

    # if reversed is specified, create reversed graph
    if (fs.has_key('reversed')): 
        reversed=True
    else:
        reversed=False
    if (reversed):
        G=G.reverse()
    searchtags=['All']
    if (fs.has_key('SearchDev')): 
     searchtags.append('Dev')
    if (fs.has_key('SearchOps')): 
     searchtags.append('Ops')
    if (fs.has_key('SearchNet')): 
     searchtags.append('Net')
    for nodeid in G.nodes():
     if (not 'searchtag' in G.node[nodeid] or not G.node[nodeid]['searchtag'] in searchtags):
      G.remove_node(nodeid)

    if (not key in G.nodes()):
        errorhtml('No Such key in given search codition') 

    ## Compute Tree from key node
    if (compute_mode=="dfs"):
     st=nx.dfs_tree(G, key) # "st" means "spanning tree"

     # add other edge if other paths are there:
     for node1 in st.nodes():
      for node2 in st.nodes():
       if G.has_edge(node1, node2):
        st.add_edge(node1,node2)

    elif (compute_mode=="distance"):
     if (graphtype == "undirectional"):
      G=nx.Graph(G)
      st=nx.Graph()
     else:
      st=nx.DiGraph()
     if (distance == None):
      paths = nx.single_source_shortest_path(G, key)
     else:
      paths = nx.single_source_shortest_path(G, key, cutoff=distance)
     for target_node in paths.keys():
      st.add_path(paths[target_node])

    elif (compute_mode=="shortestpath"):
     st=nx.DiGraph()
     try:
      for path in nx.all_shortest_paths(G, key, shortest_path_target):
       st.add_path(path)
     except(nx.exception.NetworkXNoPath):
      errorhtml('No path found in given search codition') 

    ### add attribute
    for n in st:
     tmp = st.node[n]
     tmp['name'] = n
     if (enable_ganglia):

      def server_metric_func(key):
       return ('{0}/api/metrics.php?host={1}&metric_name=load_one'.format(ganglia_url, key))
      
      def haproxy_metric_func(key):
       # 172.17.0.3-haproxy-main1081
       tmp=key.split('-')
       hostname=tmp[0]
       applname='-'.join(tmp[1:])
       return ('{0}/api/metrics.php?host={1}&metric_name={2}'.format(ganglia_url, hostname, applname))
      
      node_types=[
      {"type": "server",
      "metric_func": server_metric_func,
      "lower_bound": 2.0,
      "upper_bound": 5.0,
      },
      {"type": "haproxy-thread",
      "metric_func": haproxy_metric_func,
      "lower_bound": 5,
      "upper_bound": 15,
      }
      ]
      try:
       if (n.find('haproxy-') > -1):
        node_type = 'haproxy-thread'
       else:
        node_type = 'server'
       ctx = filter (lambda x: x["type"] == node_type, node_types) [0]
       #print (ctx)
       metric_url=ctx["metric_func"](n)
       f = urllib.urlopen(metric_url)
       js=json.loads(f.read()) # {"status":"ok","message":{"metric_value":"0.51","units":" "}}
       f.close()
       if (js['status']=='ok'):
        load_one=float(js['message']['metric_value'])
        if (ctx["upper_bound"] < load_one):
         tmp['color'] = '#ff634f'
        elif (ctx["lower_bound"] < load_one < ctx["upper_bound"]):
         tmp['color'] = '#ffde5e'
        else:
         tmp['color'] = '#e2ecff'
      except (IOError):
       pass # ganglia is not available

      #raise Exception, tmp['color']
      tmp['href'] = './node-hrefs?key={0}'.format(n)
     else: 
      if (G.node[n].has_key('color')):
       tmp['color'] = G.node[n]['color']
      if (G.node[n].has_key('href')):
       tmp['href'] = './node-hrefs?key={0}'.format(n)

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
    return ("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
                <meta charset="UTF-8">
                <title></title>
        </head>
        <body>
        <h2>Summary</h2>
        <div id="d3">

    <div id="chart"></div>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.4.11/d3.min.js"></script>
    <link type="text/css" rel="stylesheet" href="static/applconn.css"/>
    <script>var jsonpath="static/1.json";</script>
    <script type="text/javascript" src="static/applconn.js"></script>

        <a href="static/1.json">d3-graph-data</a>
        </div>

        <h2>Detail</h2>
         %s
        <div id="data">
        <a href="static/1.txt">Data</a>
        </div>
        </body>
        </html>
        """ % (svgdata)
    )


@app.route("/node-hrefs")
def node_hrefs():
    # Initialize Graph
    G=nx.DiGraph()
    with open(json_filepath) as f:
        jsondata=json.loads(f.read())
        G=json_graph.node_link_graph(jsondata)

    fs=request.args # when GET, use this

    if (not fs.has_key('key')):
     errorhtml('No key defined')
    key=fs['key']
    if (not key in G.nodes()):
     errorhtml('No Such key') 

    # create urls:
    urls = []

    # default url
    if (G.node[key].has_key('href')):
     urls.append(G.node[key]['href'])
    # ganglia url
    if (settings.enable_ganglia):
     if (key.find('_cpu') > -1):
      urls.append('{0}/graph_all_periods.php?hreg%5B%5D={1}&mreg%5B%5D=cpu_&aggregate=1'.format(ganglia_url, key[:-4]))
     elif (key.find('-haproxy') > -1):
      urls.append('{0}/graph_all_periods.php?hreg%5B%5D={1}&mreg%5B%5D=haproxy&aggregate=1'.format(ganglia_url, key.split('-')[0]))
     else:
      urls.append('{0}?c=unspecified&h={1}'.format(ganglia_url, key))
    # kibana url
    if (settings.enable_elasticsearch):
     urls.append('{0}{1}?id={2}'.format(kibana_url, key, G.node[key]['kibanaid']))

    # if only one url is found, return that
    if (len(urls) == 1):
     return (redirect(urls[0], code=302))

    # join urls
    urlhtml='<br/>'.join(
     '<a href="{0}">link</a>'.format(url) for url in urls
    )

    ## CGI
    return ("""
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


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
