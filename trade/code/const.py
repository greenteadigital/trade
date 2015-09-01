import os

# # Funcs
pjoin = os.path.join
pexists = os.path.exists

# # Directories
HOME = os.environ['HOME']
DTOP = pjoin(HOME, 'Desktop')
WSPACE = pjoin(HOME, 'eclipse-workspace')

PROJ_DIR = pjoin(WSPACE, 'trade')
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
