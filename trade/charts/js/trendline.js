var trendline;

function enableTrendLine() {

	var annotate = d3.select("#annotationGroup");
	
	annotate.on('mousedown', mousedown)
		.on('mouseup', mouseup);
	
	function mousedown() {
	    var m = d3.mouse(this);
	    trendline = annotate.append("line")
	        .attr("x1", m[0])
	        .attr("y1", m[1])
	        .attr("x2", m[0])
	        .attr("y2", m[1])
	        .attr('class', 'trendline');
	
	    annotate.on("mousemove", mousemove);
	}

	function mousemove() {
		var m = d3.mouse(this);
	    trendline.attr("x2", m[0])
	        .attr("y2", m[1]);
	}
	
	function mouseup() {
		annotate.on("mousemove", null);
	}
}