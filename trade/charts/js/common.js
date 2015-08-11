var log = console.log,
dataServer = 'http://localhost',
w = window,
d = document,
e = d.documentElement,
g = d.getElementsByTagName('body')[0],
cwidth = w.innerWidth || e.clientWidth || g.clientWidth,
cheight = w.innerHeight|| e.clientHeight|| g.clientHeight,
margin = 35,
zoomMult = 1;

function queryParams() {
	var out = {},
	search = location.search.substr(1).split('&');
	
	for (idx in search) {
		var kv = search[idx].split('=')
		var k = kv[0];
		var v = kv[1];
		out[k] = v;
	}
	return out;
}
