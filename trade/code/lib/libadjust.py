
def yAdjust(data):
	''' Adjust OHLC values using Y! provided Adj Close  '''
	mult = float(data['Adj Close']) / float(data['Close'])
	data['Open'] = float(data['Open']) * mult 
	data['High'] = float(data['High']) * mult
	data['Low'] = float(data['Low']) * mult
	data['Close'] = float(data['Close']) * mult
	data['Volume'] = int(data['Volume']) / mult
	