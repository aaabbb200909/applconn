# applconn
import rsync+git to create JSON (optionally visualize with networkx+graphviz, search with Kibana)

# Install
(Procedure is for CentOS7):
~~~~
$ sudo yum install graphviz graphviz-devel gcc python-devel
$ sudo pip install networkx pygraphviz flask requests
$ cd /var/tmp && git clone https://github.com/aaabbb200909/applconn.git && cd applconn
$ ./batchregister.py # create test json
$ ./applconn.py

Then access this URL
http://127.0.0.1:5000

you can also try docker
$ sudo docker run -it tnaganawa/applconn
or kubernetes
$ sudo kubectl create -f ./pod.yaml
~~~~

# Usage
https://github.com/tnaganawa/applconn/wiki

# Reference
blog (written in Japanese)  
http://aaabbb-200904.hatenablog.jp/archive/category/applconn

