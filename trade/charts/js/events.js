// EVENTS

window.onhashchange = window.onload = function() {
	d3.selectAll("svg").remove();
	candleData = undefined;		
	fetchData();
}

d3.select("#daysPer")
	.on("change", function(d, i) {
		d3.selectAll("svg").remove();
		daysPerCandle = d3.event.target.valueAsNumber;
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