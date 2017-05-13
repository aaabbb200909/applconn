FROM centos:7
RUN yum install -y python-setuptools git graphviz graphviz-devel gcc python-devel && easy_install pip && pip install -U networkx pygraphviz flask requests && cd /var/tmp && git clone https://github.com/tnaganawa/applconn && chmod 777 /var/tmp/applconn/ && cd /var/tmp/applconn/ && ./batchregister.py
RUN yum install -y epel-release && yum install -y ganglia-gmond ganglia-gmetad ganglia-web && sed -i 's/ bind =.*/ bind = 0.0.0.0/' /etc/ganglia/gmond.conf && sed -i 's/Require local/Require all granted/' /etc/httpd/conf.d/ganglia.conf && cd /var/tmp/applconn/ && git pull && true
EXPOSE 5000 80
CMD ["/bin/bash", "-c", "cd /var/tmp/applconn; ./entrypoint.sh"]
