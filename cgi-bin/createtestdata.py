#!/usr/bin/env python
from redis import *
r=Redis()

## Populate Data
#G.add_node('1', label='xxx', shape='box', color='red', style='filled', fontcolor='#ffffff')
r.sadd('nodes', '2')
r.sadd('nodes', '3')

r.sadd('edges', ('1','2'))
r.sadd('edges', ('2','3'))

tmp=["Portugal","Spain","France","Germany","Belgium","Netherlands","Italy"]+ ["Switzerland","Austria","Denmark","Poland","Czech Republic","Slovakia","Hungary"]+ ["England","Ireland","Scotland","Wales"]
for i in tmp:
 r.sadd('nodes', i)


r.sadd('edges',("Portugal", "Spain"))
r.sadd('edges',("Spain","France"))
r.sadd('edges',("France","Belgium"))
r.sadd('edges',("France","Germany"))
r.sadd('edges',("France","Italy"))
r.sadd('edges',("Belgium","Netherlands"))
r.sadd('edges',("Germany","Belgium"))
r.sadd('edges',("Germany","Netherlands"))
r.sadd('edges',("England","Wales"))
r.sadd('edges',("England","Scotland"))
r.sadd('edges',("Scotland","Wales"))
r.sadd('edges',("Switzerland","Austria"))
r.sadd('edges',("Switzerland","Germany"))
r.sadd('edges',("Switzerland","France"))
r.sadd('edges',("Switzerland","Italy"))
r.sadd('edges',("Austria","Germany"))
r.sadd('edges',("Austria","Italy"))
r.sadd('edges',("Austria","Czech Republic"))
r.sadd('edges',("Austria","Slovakia"))
r.sadd('edges',("Austria","Hungary"))
r.sadd('edges',("Denmark","Germany"))
r.sadd('edges',("Poland","Czech Republic"))
r.sadd('edges',("Poland","Slovakia"))
r.sadd('edges',("Poland","Germany"))
r.sadd('edges',("Czech Republic","Slovakia"))
r.sadd('edges',("Czech Republic","Germany"))
r.sadd('edges',("Slovakia","Hungary"))
