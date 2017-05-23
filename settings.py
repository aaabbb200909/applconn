json_filepath="/var/tmp/applconn/static/applconn.json"
pathprefix='/var/tmp/applconn/static'
rsyncgitpath='/var/tmp/rsyncgit/'

##

list_import_def=[
    #"import_ansible_facts",
    #"import_haproxy",
    "import_testlogic"
]

##
enable_ganglia=False
enable_elasticsearch=False
enable_prometheus=False

ganglia_url='http://127.0.0.1/ganglia/'
elasticsearchurl='127.0.0.1:9200'
kibana_url='http://127.0.0.1:5601/app/kibana#/doc/*/applconn/'
prometheus_url='http://127.0.0.1:9090/'


# override settings if local_settings.py is there
try:
 from local_settings import *
except ImportError as e:
 pass
