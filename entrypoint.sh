#!/bin/bash
gmetad
gmond
httpd
cd /var/tmp/applconn/
python -m CGIHTTPServer
