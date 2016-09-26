#!/usr/bin/env python
# -*- coding: utf-8 -*-
from redis import *
import cgi,os,sys
from util import *

f=cgi.FieldStorage()

r=Redis()
if (f.has_key('key')):
 key=f['key'].value
 if (r.sismember('nodes', key)):
  errorhtml(key + ' is already there')
 else:
  r.sadd('nodes', key)
elif(f.has_key('key1') and f.has_key('key2')):
 key1=f['key1'].value
 key2=f['key2'].value
 tmp=(key1, key2)
 if (r.sismember('edges', tmp)):
  errorhtml(repr(tmp) + ' is already there')
 r.sadd('edges', tmp)

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
データを保管しました。
</body>
</html>
"""

