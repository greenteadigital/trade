
var buildCandles = function(data) {
	
	var width = cwidth;
	var height = cheight;
	
	
	var chart = d3.select("div.candlesticks")
		.append("svg")
		.attr("width", width)
		.attr("height", height)
		.attr("id", "candleSvg");
	
	var gridLayer = chart.append("g");
	var volumeLayer = chart.append("g");
	var candleLayer = chart.append("g")
		.attr('id', 'candleLayer');
	
	// Set up annotation layer for later use by trendlines, etc.
	chart.append("g")
		.attr('id', 'annotationGroup')
		.append("rect")
		.attr("width", width)
		.attr("height", height)
		.attr('id', 'annotationRect');
	
	var minY = d3.min(data.map(function(d) { return +d.Low; }));
	var maxY = d3.max(data.map(function(d) { return +d.High; }))
	
	var y = d3.scale.linear()
		.domain([0.99*minY, 1.01*maxY])
		.range([height - margin, margin]);
	
	var x = d3.scale.linear()
		.domain([0, data.length])
		.range([width - margin - (data.length * candleWidth) - ((data.length - 1) * candleSpacing), width - margin]);
	
	gridLayer.selectAll("line.xTick")
		.data(x.ticks())
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
		.data(x.ticks())
		.enter().append("text")
		.attr("x", x)
		.attr("y", height - margin)
		//.attr("dy", 20)
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
		.text(function(d){ return d3.round(d, 2) });

	function setColor(d, i) {
		if (i > 0) {
			return +d.Close > +data[i-1].Close ? "black" : red;
		} else if (i == 0) {
			return +d.Close > +d.Open ? "black" : red;
		}
	}

	function setWickX(d, i) { return x(i) - (candleWidth/2.0) - candleSpacing }
	
	// draw volume
	drawVolume = function() {
		volumeLayer.selectAll(".volumeBar").remove();
		var volume = volumeLayer.selectAll(".volumeBar").data(data);
		
		volume.enter()
			.append("rect")
			.attr("x", function(d, i) { return x(i) - (candleWidth + candleSpacing) })
			.attr("y", function(d) { return height - margin - +d.Volume*volmult/daysPerCandle })
			.attr("height", function(d) { return +d.Volume*volmult/daysPerCandle })
			.attr("width", candleWidth)
			.attr("class", "volumeBar")
			.attr("fill", setColor)
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
		.attr("stroke", setColor)
		.attr("id", function(d) { return "candle" + d.Date });
	
	// draw candles
	candle.append("rect")
		.attr("x", function(d, i) { return x(i) - (candleWidth + candleSpacing) })
		.attr("y", function(d) { return y(d3.max([+d.Open, +d.Close])) })		  
		.attr("height", function(d) { return d3.max([0.1, Math.abs(y(+d.Open) - y(+d.Close))]) })
		.attr("width", candleWidth)
		.attr("stroke", setColor)
		.attr("fill", function(d, i) { return +d.Close > +d.Open  ? "white" : d3.select("#candle" + d.Date).attr("stroke") })
		.attr("title", function(d) {
			return d.Date
			+ " O:" + d.Open
			+ " H:" + d.High
			+ " L:" + d.Low
			+ " C:" + d.Close
			+ " V:" + d.Volume
			});
	
	window.scrollTo(scrollMaxX, 0);	
	enableTrendLine();
	
	d3.json(dataServer
			+ '/obv.json'
			+ '?symbol=' + location.hash.substr(1)
			+ '&depth=' + histDepth
			+ '&dpc=' + daysPerCandle,
			buildObv);
}
