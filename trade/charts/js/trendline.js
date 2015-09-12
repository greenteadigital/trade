var trendline;
//STILLBROKEN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
function enableTrendLine() {
	log('in enableTrendLine')
	var annotate = d3.select("#annotationLayer");
	
	function mousedown() {
		log('mousedown');
	    var m = d3.mouse(this);
	    trendline = annotate.append("line")
	        .attr("x1", m[0])
	        .attr("y1", m[1])
	        .attr("x2", m[0])
	        .attr("y2", m[1]);
	
	    annotate.on("mousemove", mousemove);
	}

	function mousemove() {
		log('mousemove');
		var m = d3.mouse(this);
	    trendline.attr("x2", m[0])
	        .attr("y2", m[1]);
	}
	
	function mouseup() {
		log('mouseup');
		annotate.on("mousemove", null);
	
	annotate.on("mousedown", mousedown)
    	.on("mouseup", mouseup);
	
	}
}