
var buildCandles = function(data) {

	var width = zoomMult * d3.max([data.length * daysPerCandle, cwidth]);
	var height = zoomMult * cheight;
	
	var chart = d3.select("div.candlesticks")
		.append("svg")
		.attr("width", width)
		.attr("height", height);
	
	var gridLayer = chart.append("g");
	var volumeLayer = chart.append("g");
	var candleLayer = chart.append("g");
	
	var y = d3.scale.linear()
		.domain([0, d3.max(data.map(function(d) { return +d.High; }))])
		.range([height - margin, margin]);
	
	var x = d3.scale.linear()
		.domain([data.length, 0])
		.range([margin, width - margin]);
	
	var dates = data.map(function(d) {return new Date(d.Date)});
	var first = d3.min(dates);
	var last = d3.max(dates);
	var days = (last.getTime() - first.getTime())/1000/60/60/24;
	
	var xTicks = width/100;
	
	gridLayer.selectAll("line.xTick")
		.data(x.ticks(xTicks))
		.enter().append("line")
		.attr("x1", x)
		.attr("x2", x)
		.attr("y1", margin)
		.attr("y2", height - margin)
		.attr("stroke", "#ccc");

	gridLayer.selectAll("line.yTick")
		.data(y.ticks(yTicks))
		.enter().append("line")
		.attr("x1", margin)
		.attr("x2", width - margin)
		.attr("y1", y)
		.attr("y2", y)
		.attr("stroke", "#ccc");

	gridLayer.selectAll("text.xLabel")
		.data(x.ticks(xTicks))
		.enter().append("text")
		.attr("x", x)
		.attr("y", height - margin)
		.attr("dy", 20)
		.attr("text-anchor", "middle")
		.text(function(d) { return d.Date; });

	gridLayer.selectAll("text.yLabel")
		.data(y.ticks(yTicks))
		.enter().append("text")
		.attr("x", width - margin)
		.attr("y", y)
		.attr("dy", 5)
		.attr("dx", 20)		 
		.attr("text-anchor", "middle")
		.text(String);

	function setClass(d) { return +d.Close > +d.Open ? "up" : "down" }
	function setWickX(d, i) { return x(i) }
	function getRectWidth(d) { return (0.5 * (width - 2*margin) / data.length).toFixed(4) }
	
	// draw volume
	drawVolume = function() {
		volumeLayer.selectAll(".volumeBar").remove();
		var volume = volumeLayer.selectAll(".volumeBar").data(data);
		
		volume.enter()
			.append("rect")
			.attr("x", function(d, i) { return x(i) - getRectWidth()/2 })
			.attr("y", function(d) { return height - margin - +d.Volume*volmult/daysPerCandle })
			.attr("height", function(d) { return +d.Volume*volmult/daysPerCandle })
			.attr("width", getRectWidth)
			.attr("class", function(d) { return "volumeBar " + setClass(d) })
			.attr("title", function(d) { return d.Date + " Vol: " + d.Volume });
	}
	drawVolume();
	
	var candle = candleLayer.selectAll("candles")
	  .data(data)
	  .enter();
	
	// draw hi/lo 'wicks'
	candle.append("line")
		.attr("x1", setWickX)
		.attr("x2", setWickX)			
		.attr("y1", function(d) { return y(+d.High) })
		.attr("y2", function(d) { return y(+d.Low) })
		.attr("class", setClass)
		.attr("id", function(d) { return "candle" + d.Date });
	
	// draw candles
	candle.append("rect")
		.attr("x", function(d, i) { return x(i) - getRectWidth()/2 })
		.attr("y", function(d) { return y(d3.max([+d.Open, +d.Close])) })		  
		.attr("height", function(d) { return d3.max([0.1, Math.abs(y(+d.Open) - y(+d.Close))]) })
		.attr("width", getRectWidth)
		.attr("class", setClass)
		.attr("title", function(d) {
			return d.Date
			+ " O:" + d.Open
			+ " H:" + d.High
			+ " L:" + d.Low
			+ " C:" + d.Close
			+ " V:" + d.Volume
			});
}
