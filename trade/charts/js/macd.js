// MACD params
var fast = '13',
slow = '26',
signal = '9',
macdPoints = false,
macdHisto = true,
sigPoints = false;

var buildMacd = function(data) {
	
	if (data.length > histDepth) {
		var data = data.slice(data.length - histDepth, data.length);
	}
	var height = 150,
	width = d3.select("#candleSvg").attr("width"),
	macdVals = data.map(function(d) { return d.MACD; }),
	yExaggerate = 50,
	interp = "monotone";
	
	var chart = d3.select("div.macd")
		.append("svg")
		.attr("width", width)
		.attr("height", height)
		.attr("id","macdSvg");
	
	var gridLayer = chart.append("g");
	var sigLayer = chart.append("g");
	var macdLayer = chart.append("g");
	
	var y = d3.scaleLinear()
		.domain([d3.min(macdVals), d3.max(macdVals)])
		.range([height-margin, 1]);
		
	gridLayer.selectAll(".macdZero")
		.data([0])
		.enter().append("line")
		.attr("x1", margin)
		.attr("x2", width - margin)
		.attr("y1", y)
		.attr("y2", y)
		.attr("class", "macdZero");
		
	var macdLine = d3.line()
		.x(function(d) { var selStr = "#candle"+d.Date;
			//log(selStr)
			var sel = d3.select(selStr);
			//log(sel);
			return sel.attr("x1");
			})
		.y(function(d) { return y(d.MACD); })
		.curve(d3.curveMonotoneX);
		
	macdLayer.append("path")
		.attr("d", macdLine(data))
		.attr("stroke", "red")
		.attr("stroke-width", 1)
		.attr("fill", "none")
		.attr("class", "macdPath");
		
	var sigLine = d3.line()
		.x(function(d) { return d3.select("#candle"+d.Date).attr("x1"); })
		.y(function(d) { return y(d.Sig); })
		.curve(d3.curveMonotoneX);
		
	sigLayer.append("path")
		.attr("d", sigLine(data))
		.attr("stroke", "blue")
		.attr("stroke-width", 1)
		.attr("fill", "none")
		.attr("class", "sigPath");
	
	drawMacdHisto = function() {
		var histo = gridLayer.selectAll(".histo");
		
		if (macdHisto) {
			histo.data(data)
				.enter()
				.append("rect")
				.attr("x", function(d) { return d3.select("#candle"+d.Date).attr("x1") })
				.attr("y", function(d) {
					var s = d3.select(".macdZero").attr("y1");
					return d.MACD < d.Sig ? s : s - (d.d * yExaggerate);
					})
				.attr("width", candleWidth)
				.attr("height", function(d) { return d.d * yExaggerate })
				.attr("class", function(d) { return d.MACD < d.Sig ? "histo neg" : "histo pos" });
		} else {
			histo.remove();
		}
	}
	
	addSigPoints = function() {
		var points = sigLayer.selectAll(".sigPoints");
		
		if (sigPoints) {
			points.data(data)
				.enter()
				.append("circle")
				.attr("cx", function(d) { return d3.select("#candle"+d.Date).attr("x1"); })
				.attr("cy", function(d) { return y(d.Sig) })
				.attr("r", 2)
				.attr("title", function(d) { return d.Date + " Signal: " + d.Sig + "" })
				.attr("class","sigPoints point");
		} else {
			points.remove();
		}
	}
	
	addMacdPoints = function() {
		var points = macdLayer.selectAll(".macdPoints");
		
		if (macdPoints) {
			points.data(data)
				.enter()
				.append("circle")
				.attr("cx", function(d) { return d3.select("#candle"+d.Date).attr("x1"); })
				.attr("cy", function(d) { return y(d.MACD) })
				.attr("r", 2)
				.attr("stroke", "orange")
				.attr("stroke-width", 2)
				.attr("fill", "black")
				.attr("title", function(d) { return d.Date + " MACD: " + d.MACD + "" })
				.attr("class", "macdPoints point");
		} else {
			points.remove();
		}
	}
	
	if (macdPoints) {
		addMacdPoints(data);
	}
	if (sigPoints) {
		addSigPoints(data);
	}
	if (macdHisto) {
		drawMacdHisto(data);
	}
}