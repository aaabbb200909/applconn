FROM centos:7
RUN yum install -y python-setuptools git graphviz graphviz-devel gcc python-devel && easy_install pip && pip install -U networkx pygraphviz flask requests && cd /var/tmp && git clone https://github.com/tnaganawa/applconn && chmod 777 /var/tmp/applconn/ && cd /var/tmp/applconn/ && ./batchregister.py
EXPOSE 5000
CMD ["/bin/bash", "-c", "cd /var/tmp/applconn; ./entrypoint.sh"]
