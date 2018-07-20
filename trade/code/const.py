import os
from cStringIO import StringIO

# # Funcs
pjoin = os.path.join
pexists = os.path.exists
pisfile = os.path.isfile
pisdir = os.path.isdir
strio = StringIO

# # Directories
HOME = os.environ['HOME']
DTOP = pjoin(HOME, 'Desktop')
WSPACE = pjoin(HOME, 'Documents/eclipse-workspace')

PROJ_DIR = pjoin(WSPACE, 'trade/trade')
DATA_DIR = pjoin(PROJ_DIR, 'data')

SYM_DIR = pjoin(DATA_DIR, 'symbols')
DB_DIR = pjoin(DATA_DIR, 'sqlite')
SPLIT_DIR = pjoin(DATA_DIR, 'splits')
JSON_DIR = pjoin(DATA_DIR, 'json')
EOD_DIR = pjoin(DATA_DIR, 'eod')

RAW_DIR = pjoin(EOD_DIR, 'raw')
ADJ_DIR = pjoin(EOD_DIR, 'adj')

if __name__ == '__main__':
	loc = locals().copy()
	for l in filter(lambda n: n.isupper(), loc):
		print l, eval("os.path.exists(%s)" % l)
