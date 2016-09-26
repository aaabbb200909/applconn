
import sys

#
pathprefix='/var/www/html/applconn/'

def errorhtml(txt):
 print "Content-Type: text/plain"
 print
 print 'Error:'
 print txt
 sys.exit(31)
