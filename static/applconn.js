var w = 400,
    h = 400,
    fill = d3.scale.category20();

var vis = d3.select("#chart")
  .append("svg:svg")
    .attr("width", w)
    .attr("height", h);

d3.json(jsonpath, function(json) {
  var force = d3.layout.force()
      .charge(-120)
      .linkDistance(30)
      .nodes(json.nodes)
      .links(json.links)
      .size([w, h])
      .start();


  var link = vis.selectAll("line.link")
      .data(json.links)
    .enter().append("svg:line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); })
      .attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

  var rect = vis.selectAll("xxx").data(json.nodes).enter()
  .append("svg:rect")
  .filter(function(d) {return d.searchtag == "All"})
  .attr("x", function(d) { return d.x; })
  .attr("y", function(d) { return d.y; })
  .attr("width", "30")
  .attr("height", "30")
  .style("fill", function(d) { return d.color; })
  .call(force.drag);
  ;

  var node = vis.selectAll("circle.node")
      .data(json.nodes)
      .enter().append("svg:circle")
      .attr("class", "node")
      .attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; })
      .attr("r", 5)
      .style("fill", function(d) { return d.color; })
      .call(force.drag);

  node.append("svg:title")
      .text(function(d) { return d.name; });

  vis.style("opacity", 1e-6)
    .transition()
      .duration(1000)
      .style("opacity", 1);

  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });

    rect.attr("x", function(d) { return d.x; })
        .attr("y", function(d) { return d.y; });
  });

});

