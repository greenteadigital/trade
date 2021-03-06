var obvPoints = false,
fullObvData;

function buildObv(data) {
	
	if (data.length > histDepth) {
		var data = data.slice(data.length - histDepth, data.length);
	}

	var height = 150,
	width = d3.select("#candleSvg").attr("width"),
	obvVals = data.map(function(d) { return d.OBV } ),
	yExaggerate = 1,
	interp = "linear";
	
	var chart = d3.select("div.obv")
		.append("svg")
		.attr("width", width)
		.attr("height", height)
		.attr("id", "obvSvg");
	
	var gridLayer = chart.append("g");
	var obvLayer = chart.append("g");
	
	var y = d3.scaleLinear()
		.domain([d3.min(obvVals) * yExaggerate, d3.max(obvVals) * yExaggerate])
		.range([height - 1, 1]);
	
	gridLayer.selectAll(".obvZero")
		.data([0])
		.enter().append("line")
		.attr("x1", margin)
		.attr("x2", width - margin)
		.attr("y1", y)
		.attr("y2", y)
		.attr("class", "obvZero");
	
	var obvLine = d3.line()
		.x(function(d) { var selStr = "#candle"+d.Date;
			//log(selStr)
			var sel = d3.select(selStr);
			//log(sel);
			return sel.attr("x1");
			})
		.y(function(d) { return y(d.OBV * yExaggerate); })
		.curve(d3.curveLinear);
		
	obvLayer.append("path")
		.attr("d", obvLine(data))
		.attr("class", "obvLine");
	
	addObvPoints = function() {
		var points = obvLayer.selectAll(".obvPoints");
		
		if (obvPoints) {
			points.data(data).enter()
				.append("circle")
				.attr("cx", function(d) { return d3.select("#candle"+d.Date).attr("x1"); })
				.attr("cy", function(d) { return y(d.OBV * yExaggerate) })
				.attr("r", 2)
				.attr("title", function(d) { return d.Date + " OBV: " + d.OBV + "" })
				.attr("class", "obvPoints point");
		} else {
			points.remove();
		}
	}
	
	if (obvPoints) {
		addObvPoints(data);
	}
	
	d3.json(dataServer
			+ '/macd.json'
			+ '?fast=' + fast
			+ '&slow=' + slow
			+ '&symbol=' + location.hash.substr(1)
			+ '&signal=' + signal
			+ '&depth=' + histDepth
			+ '&dpc=' + daysPerCandle,
			buildMacd);

}