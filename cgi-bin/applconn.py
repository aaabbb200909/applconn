#!/usr/bin/env python
# -*- coding: utf-8 -*-
from networkx import *
from redis import *
import cgi,os,sys
from util import *

# Initialize Graph
G=DiGraph()


r=Redis()
G.add_nodes_from(r.smembers('nodes'))
tmp=[]
for s in r.smembers('edges'):
 tmp.append((eval(s)))
G.add_edges_from(tmp)


def drawimage(filename):
 os.system('dot -Tsvg %s/%s.txt -o %s/%s.svg' % (pathprefix, filename,
    pathprefix, filename))

## Write down all the data
A=to_agraph(G)
A.write(pathprefix+'a.txt')
drawimage('a')


##
f=cgi.FieldStorage()
if (not f.has_key('key')):
 errorhtml('No key defined')
key=f['key'].value
if (f.has_key('reversed')): 
 reversed=True
else:
 reversed=False
 



if (not key in G):
 errorhtml('No Such key')



## Compute Spanning Tree

##reversed=True
if (reversed):
 G=G.reverse()
st=dfs_tree(G, key)

## add attribute
#st.node['1']['color']='red'
#st.node['1']['URL']='http://www.google.co.jp'
#st['1']['2']['color']='blue'



## Graphviz
A=to_agraph(st)
A.write('%(pathprefix)s/1.txt' % locals())


## SVG
drawimage('1')

## inline svg
svgfile=file(pathprefix+'/1.svg')
svgdata=svgfile.read()
svgfile.close()

## CGI
print "Content-Type: text/html"
print

print """
<!DOCTYPE html>
<html lang="en">
<head>
        <meta charset="UTF-8">
        <title></title>
</head>
<body>
<h2>graph</h2>
 %s
<!--
<a href="../1.svg">
 <img src="../1.svg" alt="" />
</a>
-->
<div id="data">
<a href="../1.txt">データ</a>
</div>
</body>
</html>
""" % (svgdata)

