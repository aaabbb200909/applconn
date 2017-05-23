#!/usr/bin/python
import cgi
import os
import sys
import json
import urllib
import requests
import networkx as nx
from networkx.readwrite import json_graph
from flask import Flask, render_template, url_for, request, redirect
import settings

app = Flask(__name__)

enable_ganglia=settings.enable_ganglia
ganglia_url=settings.ganglia_url
enable_prometheus=settings.enable_prometheus
prometheus_url=settings.prometheus_url
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
     if (enable_ganglia or settings.enable_prometheus):

      def get_url_for_server_metric_func_ganglia(key):
       return ('{0}/api/metrics.php?host={1}&metric_name=load_one'.format(ganglia_url, key))

      def get_url_for_haproxy_metric_func_ganglia(key):
       # 172.17.0.3-haproxy-main1081
       tmp=key.split('-')
       hostname=tmp[0]
       applname='-'.join(tmp[1:])
       return ('{0}/api/metrics.php?host={1}&metric_name={2}'.format(ganglia_url, hostname, applname))
       
      def tmp_metric_func_ganglia(key, kind_of_node):
       if (kind_of_node == "server"):
        metric_url = get_url_for_server_metric_func_ganglia(key)
       elif (kind_of_node == "haproxy"):
        metric_url = get_url_for_haproxy_metric_func_ganglia(key)
       else:
        Exception("No Such kind_of_node: {0}", kind_of_node)
       f = urllib.urlopen(metric_url)
       js=json.loads(f.read()) # {"status":"ok","message":{"metric_value":"0.51","units":" "}}
       f.close()
       #print (js)
       if (js['status']=='ok'):
        load_one=float(js['message']['metric_value'])
       else:
        load_one=0 # hmm ...
       return load_one

      def server_metric_func_ganglia(key):
       return tmp_metric_func_ganglia(key, "server")
      def haproxy_metric_func_ganglia(key):
       return tmp_metric_func_ganglia(key, "haproxy")

      def tmp_metric_func_prometheus(key, kind_of_node):
       # TODO: return value is json, not float
       if (kind_of_node == "server"):
        metric_url='{0}/api/v1/query?query=node_load1{{instance="{1}:9100"}}'.format(prometheus_url, key)
       elif (kind_of_node == "haproxy"):
        tmp=key.split('-')
        nodename=tmp[0]
        applname=tmp[2]
        metric_url='{0}/api/v1/query?query=haproxy_frontend_current_sessions{{frontend="{1}",instance="{2}:9101"}}'.format(prometheus_url, applname, nodename)
       else:
        Exception("No Such kind_of_node: {0}", kind_of_node)
       returned = requests.get(metric_url)
       js=json.loads(returned.content) # {"status":"success","data":{"resultType":"vector","result":[{"metric":{"__name__":"node_load1","instance":"172.17.0.3:9100","job":"prometheus"},"value":[1495462713.021,"0.91"]}]}}
       #print (js)
       if (js['status']=='success'):
        if (len(js['data']['result']) > 0):
         load_one=float(js['data']['result'][0]["value"][1])
        else:
         load_one=0 # hmmm ...
       else:
        load_one=0 # hmm ...
       return load_one

      def server_metric_func_prometheus(key):
       return tmp_metric_func_prometheus(key, "server")
      
      def haproxy_metric_func_prometheus(key):
       return tmp_metric_func_prometheus(key, "haproxy")
      
      if (settings.enable_ganglia):
       server_metric_func=server_metric_func_ganglia
       haproxy_metric_func=haproxy_metric_func_ganglia
      if (settings.enable_prometheus):
       server_metric_func=server_metric_func_prometheus
       haproxy_metric_func=haproxy_metric_func_prometheus

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
       load_one=ctx["metric_func"](n)
       #print (load_one)
       if (ctx["upper_bound"] < load_one):
        tmp['color'] = '#ff634f'
       elif (ctx["lower_bound"] < load_one < ctx["upper_bound"]):
        tmp['color'] = '#ffde5e'
       else:
        tmp['color'] = '#e2ecff'
      except (IOError):
       pass # ganglia is not available
     else: 
      if (G.node[n].has_key('color')):
       tmp['color'] = G.node[n]['color']

     # set other things
     tmp['href'] = './node-hrefs?key={0}'.format(n)
     if (G.node[n].has_key('searchtag')):
      tmp['searchtag'] = G.node[n]['searchtag']

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
    if (settings.enable_prometheus):
     if (key.find('-haproxy') > -1):
      tmp=key.split('-')
      nodename=tmp[0]
      applname=tmp[2]
      urls.append('{0}/graph?g0.range_input=1h&g0.expr=haproxy_frontend_current_sessions{{instance%3D"{1}%3A9101",frontend%3D"{2}"}}&g0.tab=0'.format(prometheus_url, nodename, applname))
     else:
      urls.append('{0}/graph?g0.range_input=1h&g0.expr=node_load1{{instance%3D"{1}%3A9100"}}&g0.tab=0'.format(prometheus_url, key))

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
