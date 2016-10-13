# applconn
import rsync+git to create JSON (optionally visualize with networkx+graphviz, search with Kibana)

# Install
(Procedure is for CentOS7):
~~~~
$ git clone git@github.com:aaabbb200909/applconn.git && cd applconn

# Batch
$ sudo mkdir /usr/local/applconn
$ sudo chown apache.apache /usr/local/applconn
$ sudo chmod 777 /usr/local/applconn
$ sudo cp -i batchregister.py /usr/local/bin

# CGI
$ sudo mkdir /var/www/html/applconn
$ sudo chown apache.apache /var/www/html/applconn
$ sudo chmod 644 /var/www/html/applconn
$ sudo cp -iR cgi-bin/ index.html /var/www/html/applconn
~~~~

# Usage
https://github.com/aaabbb200909/applconn/wiki

# Reference
blog (written in Japanese) http://aaabbb-200904.hatenablog.jp/archive/category/applconn

