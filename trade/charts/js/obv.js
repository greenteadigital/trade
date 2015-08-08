var obvPoints = false

function buildObv(data) {
	var height = zoomMult * 250;
	var width = zoomMult * d3.max([data.length * daysPerCandle, cwidth]);
	var obvVals = data.map(function(d) { return d.OBV } )
	var yExaggerate = 1;
	var interp = "linear";
	
	var chart = d3.select("div.obv")
		.append("svg")
		.attr("width", width)
		.attr("height", height)
		.attr("id", "obvSvg");
	
	var gridLayer = chart.append("g");
	var obvLayer = chart.append("g");
	
	var y = d3.scale.linear()
		.domain([d3.min(obvVals) * yExaggerate, d3.max(obvVals) * yExaggerate])
		.range([height, 1]);
	
	gridLayer.selectAll(".obvZero")
		.data([0])
		.enter().append("line")
		.attr("x1", margin)
		.attr("x2", width - margin)
		.attr("y1", y)
		.attr("y2", y)
		.attr("class", "obvZero");
	
	var obvLine = d3.svg.line()
		.x(function(d) { return d3.select("#candle"+d.Date).attr("x1"); })
		.y(function(d) { return y(d.OBV * yExaggerate); })
		.interpolate(interp);
		
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
				.attr("r", 3)
				.attr("stroke", "orange")
				.attr("stroke-width", 2)
				.attr("fill", "blue")
				.attr("title", function(d) { return d.Date + " OBV: " + d.OBV + "" })
				.attr("class", "obvPoints");
		} else {
			points.remove();
		}
	}
	
	if (obvPoints) {
		addObvPoints(data);
	}

}