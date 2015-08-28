import os.path

# # Funcs
pjoin = os.path.join

# # Directories
PROJ_DIR = pjoin(os.environ['HOME'], r'eclipse-workspace\trade')
DATA_DIR = pjoin(PROJ_DIR, 'data')

FTP_DIR = pjoin(DATA_DIR, 'ftp')
DB_DIR = pjoin(DATA_DIR, 'sqlite')
SPLIT_DIR = pjoin(DATA_DIR, 'splits')
JSON_DIR = pjoin(DATA_DIR, 'json')
EOD_DIR = pjoin(DATA_DIR, 'eod')

RAW_DIR = pjoin(EOD_DIR, 'raw')
ADJ_DIR = pjoin(EOD_DIR, 'adj')
