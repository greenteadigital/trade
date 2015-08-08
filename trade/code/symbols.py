import os, json
dir_ = r".\data\csv"

def getSyms(*args):
	symbols = map(lambda f: f.split('.')[0].lstrip('_'), os.listdir(dir_))
	return json.dumps(symbols)