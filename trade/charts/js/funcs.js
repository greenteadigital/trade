var log = console.log;

var queryParams = function() {
	var out = {},
	search = location.search.substr(1).split('&');
	
	for (idx in search) {
		var kv = search[idx].split('=')
		var k = kv[0];
		var v = kv[1];
		out[k] = v;
	}
	return out;
};

var getHistDepth = function() {
	return Math.ceil((cwidth - (2 * margin)) / (candleWidth + candleSpacing)) * daysPerCandle;
};

var twoDp = function(flote) {
	return (Math.round(flote * 100) / 100).toFixed(2);
};