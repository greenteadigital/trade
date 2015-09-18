// EVENTS

window.onhashchange = window.onload = function() {
	d3.selectAll("svg").remove();
	candleData = undefined;
	fetchData();
	window.setTimeout(function() {
		var dropdown = d3.select("#symselect")
		
		dropdown.select("option[selected=selected]")
			.attr("selected", null);
	
		dropdown.select("option[value=" + location.hash.substr(1) + "]")
			.attr("selected", "selected");
	}, 500);
}

d3.select("#daysPer")
	.on("change", function(d, i) {
		d3.selectAll("svg").remove();
		daysPerCandle = d3.event.target.valueAsNumber;
		histDepth = getHistDepth();
		fetchData();
	});

d3.select("#volmult")
	.on("input", function(d, i) {
		volmult = d3.event.target.valueAsNumber;
		drawVolume();
	});

d3.select("#symselect")
	.on("change", function(d, i) {
		d3.selectAll("svg").remove();
		sym = d3.event.target.value;
		candleData = undefined;
		window.location.hash = sym;
	});

d3.select("#obvPoints")
	.on("click", function() {
		obvPoints = d3.event.target.checked;
		addObvPoints();
	});

d3.select("#macdPoints")
	.on("click", function() {
		macdPoints = d3.event.target.checked;
		addMacdPoints();
});

d3.select("#sigPoints")
	.on("click", function() {
		sigPoints = d3.event.target.checked;
		addSigPoints();
});

d3.select("#macdHisto")
	.on("click", function() {
		macdHisto = d3.event.target.checked;
		drawMacdHisto();
});

d3.select("#trendlineCtl")
	.on("click", function() {
		var g = d3.select("#annotationGroup");
		if (d3.event.target.checked) {
			g.attr('display', 'inline');
			d3.select('#rmTrendlines').attr('disabled', null);
		} else {
			g.attr('display', 'none');
			d3.select('#rmTrendlines').attr('disabled','');
//			d3.select('#annotationRect')
//				.attr('width', null)
//				.attr('height', null);
		}
	});

d3.select("#rmTrendlines")
	.on("click", function() {
		d3.selectAll('.trendline').remove();
	});