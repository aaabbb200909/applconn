#!/usr/bin/env python

import os
import sys
import glob
import json
import requests
import networkx as nx
from networkx.readwrite import json_graph
import settings

json_filepath=settings.json_filepath
elasticsearchurl=settings.elasticsearchurl
rsyncgitpath=settings.rsyncgitpath

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
     G.add_node(nodename, js, searchtag='All')

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
     G.add_node(nodename, searchtag='All')
     G.add_node(nodename+"-haproxy", searchtag='Dev')
     G.add_edge(nodename, nodename+"-haproxy")
     for app in apps:
      G.add_node(nodename+"-haproxy-"+app["name"], searchtag='Dev')
      G.add_edge(nodename+"-haproxy", nodename+"-haproxy-"+app["name"])
      G.add_edge(nodename+"-haproxy-"+app["name"], app["backend_ip"])

def import_testlogic(G):
    G.add_node('1', searchtag='All')
    G.add_node('2', searchtag='All')
    G.add_edge('1','2') 
    #
    G.add_node('172.17.0.3', searchtag='All')
    G.add_node('172.17.0.4', searchtag='All')
    G.add_node('172.17.0.0/24', searchtag='Ops')
    G.add_node('172.17.0.3_cpu', searchtag='Ops') 
    #G.add_edge('172.17.0.3','172.17.0.4')
    G.add_edge('172.17.0.0/24', '172.17.0.3')
    G.add_edge('172.17.0.0/24', '172.17.0.4')
    G.add_edge('172.17.0.3','172.17.0.3_cpu') 
    ## add attribute
    G.node['1']['color']='red'  # '#ffde5e'
    G.node['2']['color']='blue' # '#ff634f'
    G.node['1']['href']='http://www.google.co.jp'
    for n in G:
     G.node[n]['name'] = n

def import_tungsten_fabric_prouterlinkentry(G):
    with open ('/tmp/prouterlinkentry.json') as f:
      js = json.loads (f.read())
    for prouter in js:
      #print (prouter['name'])
      G.add_node(prouter['name'], searchtag='Net')
      for link in prouter['link_table']:
        #print ('  ' + link['remote_system_name'])
        if (prouter['role']=='spine'):
          #print (prouter['name'], link['remote_system_name'])
          G.add_edge (prouter['name'], link['remote_system_name'])
        elif (prouter['role']=='leaf'):
          G.add_edge (link['remote_system_name'], prouter['name'])

def import_tungsten_fabric_network_policy(G):
    network_policies=[]
    with open ('/tmp/network-policy1.json') as f:
      js = json.loads (f.read())
    network_policies.append(js.copy())
    with open ('/tmp/network-policy2.json') as f:
      js = json.loads (f.read())
    network_policies.append(js.copy())
    #print (network_policies)
    for network_policy in network_policies:
      tmp = network_policy["network_policy_entries"]["policy_rule"][0]
      src_vn = tmp["src_addresses"][0]["virtual_network"]
      dst_vn = tmp["dst_addresses"][0]["virtual_network"]
      G.add_node(src_vn, searchtag='Sdn')
      G.add_node(dst_vn, searchtag='Sdn')
      service_instances = tmp["action_list"]["apply_service"]
      if (len (service_instances) == 0):
        G.add_edge (src_vn, dst_vn)
        G.add_edge (dst_vn, src_vn)
      else:
        G.add_node (service_instances[0], searchtag='All')
        G.add_edge (src_vn, service_instances[0])
        G.add_node (service_instances[-1], searchtag='All')
        G.add_edge (dst_vn, service_instances[-1])
        for i in range(len(service_instances)):
          if (i == len(service_instances) - 1):
            break
          else:
            G.add_edge (service_instances[i], service_instances[i+1])
    ## test
    G.add_node("host01", searchtag='Ops')
    G.add_edge("host01", "default-domain:default-project:vn1-to-vn2")
    G.add_edge("vqfx191", "default-domain:default-project:vn11")
    G.add_edge("vqfx192", "default-domain:default-project:vn11")
    G.add_edge("vqfx193", "default-domain:default-project:vn11")
    G.add_edge("vqfx191", "default-domain:default-project:vn12")
    G.add_edge("vqfx192", "default-domain:default-project:vn12")
    G.add_edge("vqfx193", "default-domain:default-project:vn12")
    G.add_edge("vqfx191", "default-domain:default-project:vn1")
    G.add_edge("vqfx192", "default-domain:default-project:vn1")
    G.add_edge("vqfx193", "default-domain:default-project:vn1")
    G.add_edge("vqfx191", "default-domain:default-project:vn2")
    G.add_edge("vqfx192", "default-domain:default-project:vn2")
    G.add_edge("vqfx193", "default-domain:default-project:vn2")
    G.add_edge("vqfx194", "host01")
    G.add_edge("vqfx195", "host01")


list_import_def=settings.list_import_def

def main():
    G=nx.DiGraph()
    for funcname in list_import_def:
        func = globals()[funcname]
        func(G)
    js=json_graph.node_link_data(G)

    # ES output
    if (settings.enable_elasticsearch):
     try:
      requests.delete("http://{0}/applconn/".format(elasticsearchurl))

      for nodejson in js["nodes"]:
       returned=requests.post('http://{0}/applconn/{1}'.format(elasticsearchurl, nodejson["id"]), data=json.dumps(nodejson))
       kibanaid=json.loads(returned.content)["_id"]
       nodejson["kibanaid"]=kibanaid

     except(requests.exceptions.ConnectionError) as e:
      print ("WARN: can't connect ES")

    # json output
    with open(json_filepath,'w') as f:
        f.write(json.dumps(js, sort_keys=True, indent=4))


 
if __name__ == "__main__":
    main()
