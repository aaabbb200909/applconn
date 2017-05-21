json_filepath="/var/tmp/applconn/static/applconn.json"
#pathprefix='/var/www/html/applconn/'
pathprefix='/var/tmp/applconn/static'

##

list_import_def=[
    #"import_ansible_facts",
    #"import_haproxy",
    "import_testlogic"
]

##
enable_ganglia=False
enable_elasticsearch=False
enable_prometheus=True

#elasticsearchurl='172.17.0.5:9200'
elasticsearchurl='localhost:9200'
rsyncgitpath='/var/tmp/rsyncgit/'

#ganglia_url='http://127.0.0.1/ganglia/'
ganglia_url='http://172.17.0.2/ganglia/'
kibana_url='http://172.17.0.5:5601/app/kibana#/doc/*/applconn/'

#prometheus_url='http://127.0.0.1:9090/'
prometheus_url='http://172.17.0.2:9090/'
