#!/usr/bin/env python
from redis import *
import os,sys
r=Redis()

##rsyncgit
rsyncgitpath='/var/lib/git/rsyncbackup.git/'
l=os.popen('ls '+rsyncgitpath).readlines()
for st in l:
 tmp=st.strip()
 r.sadd('nodes', tmp)

##puppet yaml
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

## libvirt
