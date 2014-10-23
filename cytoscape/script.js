$(document).ready(function(){

  $.get(
    'http://www.corsproxy.com/api.richcitations.org/v0/papers?uri=http%3A%2F%2Fdx.doi.org%2F10.1371%252Fjournal.pone.0010502',
    function(response) {
      var r = response;

      var elements = new Object();
      
      elements.nodes = [];
      elements.edges = [];
      
      // setup root node
      var root_name = r.bibliographic.title;
      elements.nodes[0] =  { data: { id: "root", name: root_name, name_short: root_name.substring(0,20), weight: 65, faveColor: '#6FB1FC' } };

      for (i=0;i<r.references.length;i++) {
        var title = r.references[i].bibliographic.title;
        var text = r.references[i].bibliographic.text;
        var id = r.references[i].id;
        var name = "";

        // see what human-readable identifiers are available        
        if(typeof title !== 'undefined') {
          name = title;
        }
        else if (typeof text !== 'undefined') {
          name = text;
        }
        else if (typeof id !== 'undefined') {
          name = id;
        }
        
        else {
          console.log(r.references[i]); // debug
        }
        
        // add nodes
        elements.nodes[i+1] =  { data: { id: i.toString(), name: name, name_short: name.substring(0,20), weight: 65, faveColor: '#6FB1FC', width: "10" } };
        
        // add edges  
        elements.edges[i] = { data: { source: i.toString(), target: "root", faveColor: '#6FB1FC', strength: r.references[i].citation_groups.length } };
  
      } 

//    console.log(elements);
  
    $('#cy').cytoscape({
      layout: {
        name: 'cose',
        padding: 10
      },
      
      hideLabelsOnViewport : true,
      
      style: cytoscape.stylesheet()
        .selector('node')
          .css({
            'width': 'mapData(weight, 40, 80, 20, 60)',
//            'content': 'data(name)',
            'content': 'data(name_short)',
            'text-valign': 'center',
            'text-outline-width': 2,
            'text-outline-color': 'data(faveColor)',
            'background-color': 'data(faveColor)',
            'color': '#fff',
            'font-size':'10px'
          })
        .selector(':selected')
          .css({
            'border-width': 3,
            'border-color': '#333',
            'content': 'data(name)', // show full node name
            'font-size': '.5em'
          })
        .selector('edge')
          .css({
            'opacity': 0.666,
            'width': 'mapData(strength, 1, 10, 1, 20)',
            'target-arrow-shape': 'triangle',
            'source-arrow-shape': 'circle',
            'line-color': 'data(faveColor)',
            'source-arrow-color': 'data(faveColor)',
            'target-arrow-color': 'data(faveColor)'
          })
        .selector('edge.questionable')
          .css({
            'line-style': 'dotted',
            'target-arrow-shape': 'diamond'
          })
        .selector('.faded')
          .css({
            'opacity': 0.25,
            'text-opacity': 0
          }),
      
      elements: elements,
      
      ready: function(){
        window.cy = this;
        // giddy up
      }
    });
  });   
});








