#!/usr/bin/env python

###
#json_filepath="/usr/local/applconn/applconn.json"
json_filepath="/var/tmp/applconn/applconn.json"
elasticsearchurl='localhost:9200'
#elasticsearchurl='172.17.0.5:9200'
elasticsearch_path='/applconn/'
rsyncgitpath='/var/tmp/rsyncgit/'
###

import os
import sys
import glob
import json
import networkx as nx
from networkx.readwrite import json_graph

def import_rsyncgit(G):
    '''rsyncgit'''
    l=os.popen('ls '+rsyncgitpath).readlines()
    for st in l:
     tmp=st.strip()
    G.add_edge_from(tmp) 


def import_pupput_yaml(G):
    '''puppet yaml'''
    puppetservername='centos-virt11.jp.example.org'
    puppetyamlpath=rsyncgitpath+puppetservername+'/var/lib/puppet/yaml/facts/'
    nodes=os.popen('ls '+puppetyamlpath).readlines()
    for n in nodes:
     # Add Hostname
     n=n.strip()
     nodename=n[:-5] # Strip final '.yaml'
     r.sadd('nodes', nodename) 
     f=file(puppetyamlpath+n)
     l=f.readlines()
     f.close()
     for st in l:
      #print st
      st=st.strip()
      if (st.find('osfamily') > -1):
       tmp=st.split(': ')
       #print (n,tmp[1])
       r.sadd('nodes', tmp[1]) 
       r.sadd('edges', (nodename,tmp[1]))
      elif (st.find('ipaddress_') > -1 and (not st.find('ipaddress_lo') > -1)):
       # ipaddress_tun0: "10.200.200.6"
       tmp=st.split(': ')
       ipaddr=tmp[1].replace('"', '')
       interfacename=tmp[0].split('_')[1]
       nodename_iterfacename=nodename+'_'+interfacename
       r.sadd('nodes', nodename_iterfacename)
       r.sadd('edges', (nodename_iterfacename,ipaddr))
       r.sadd('edges', (nodename,nodename_iterfacename))


def import_libvirt(G):
    '''libvirt'''
    pass

def import_ansible_facts(G):
    '''import ansible facts
    create-fact command: ansible all -i /tmp/hosts -m setup -t /tmp/ansible_facts
    '''
    ansible_facts_dir='/tmp/ansible_facts/'
    for factpath in glob.glob(ansible_facts_dir+'*'):
     nodename=os.path.basename(factpath)
     with open(factpath) as f:
      js=json.loads(f.read())
     # remove some info which ES don't like
     js["ansible_facts"]["ansible_python"]["version_info"]=[]
     G.add_node(nodename, js)

def import_haproxy(G):
    '''import haproxy.cfg
    listen main1081
        bind *:1081
        server server1 172.17.0.4:1081
    '''
    haproxyfilepaths=glob.glob(rsyncgitpath + "/*/etc/haproxy/haproxy.cfg")
    for haproxycfgpath in haproxyfilepaths:
     nodename=haproxycfgpath.split("/")[-4]
     with open(haproxycfgpath) as f:
      l=f.readlines()
     apps=[]
     for st in l:
      st = st.rstrip()
      tmp=st.split()
      if (st.find("listen") > -1):
       app={}
       app["name"]=tmp[1]
      elif (st.find("bind") > -1):
       app["bind"]=tmp[1]
      elif (st.find("  server ") > -1):
       backend_ip_port=tmp[2]
       ttmp=backend_ip_port.split(':')
       #print (ttmp)
       app["backend_ip"]=ttmp[0]
       app["backend_port"]=ttmp[1]
       #
       apps.append(app)
       app=None
     # add to graph
     G.add_edge(nodename, nodename+"-haproxy")
     for app in apps:
      G.add_edge(nodename+"-haproxy", nodename+app["bind"])
      G.add_edge(nodename+app["bind"], app["backend_ip"])

def import_testlogic(G):
    G.add_node('1')
    G.add_node('2')
    G.add_edge('1','2') 
    #
    G.add_node('172.17.0.3')
    G.add_node('172.17.0.4')
    #G.add_edge('172.17.0.3','172.17.0.4')
    G.add_edge('172.17.0.3','172.17.0.3_cpu') 
    ## add attribute
    G.node['1']['color']='red'  # '#ffde5e'
    G.node['2']['color']='blue' # '#ff634f'
    G.node['1']['href']='http://www.google.co.jp'
    for n in G:
     G.node[n]['name'] = n

list_import_def=[
#    import_ansible_facts,
#    import_haproxy,
    import_testlogic
]


def main():
    G=nx.DiGraph()
    for func in list_import_def:
        func(G)
    js=json_graph.node_link_data(G)

    # json output
    with open(json_filepath,'w') as f:
        f.write(json.dumps(js, sort_keys=True, indent=4))

    # ES output
    os.system("curl --max-time 15 -XDELETE http://%s/applconn/" % (elasticsearchurl))
    for nodejson in js["nodes"]:
        os.system("curl --max-time 15 -XPOST http://%s/applconn/%s -d '%s'" % (elasticsearchurl, nodejson["id"], json.dumps(nodejson)))

 
if __name__ == "__main__":
    main()
