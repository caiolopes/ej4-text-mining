$(function() {
  function createHeatMap(data) {
    var config = {
      "radius": 50,
      "scaleRadius": true,
      "useLocalExtrema": true,
    };

    var baseLayer = L.tileLayer(
      'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '...',
        maxZoom: 18
      }
    );

    var map = new L.Map('map', {
      layers: [baseLayer]
    });

    map.setView([-22.0087082, -47.8909263], 4);

    var heat = L.heatLayer(data).addTo(map);
  }

  $.getJSON("http://localhost:8000/heatmap.json", function(data) {
    createHeatMap(data);
  });

  function drawWordCloud(word_count, width, height) {
    var svg_location = "#chart";
    width = width || 500;
    height= height || 500;

    var fill = d3.scaleOrdinal(d3.schemeCategory10);

    var word_entries = d3.entries(word_count);

    var xScale = d3.scaleLinear()
      .domain([0, d3.max(word_entries, function(d) {
        return d.value;
      })
      ])
      .range([10,100]);

    console.log(d3.layout);
    d3.layout.cloud().size([width, height])
      .timeInterval(20)
      .words(word_entries)
      .fontSize(function(d) { return xScale(+d.value); })
      .text(function(d) { return d.key; })
      .rotate(function() { return ~~(Math.random() * 2) * 90; })
      .font("Impact")
      .on("end", draw)
      .start();

    function draw(words) {
      d3.select(svg_location).append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + [width >> 1, height >> 1] + ")")
        .selectAll("text")
        .data(words)
        .enter().append("text")
        .style("font-size", function(d) { return xScale(d.value) + "px"; })
        .style("font-family", "Impact")
        .style("fill", function(d, i) { return fill(i); })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { return d.key; });
    }

    d3.layout.cloud().stop();
  }

  drawWordCloud({
    'caio': 10,
    'lopes': 8,
    'pri': 5
  });
});


