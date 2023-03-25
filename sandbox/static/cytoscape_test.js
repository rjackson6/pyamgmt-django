import cytoscape from "{% static 'cytoscape.esm.min.js' %}"; // Copied from a template

window.cy = cytoscape({
    container: document.getElementById('cy'),
    elements: [
        {
            data: {id: 'a'}
        },
        {
            data: {id: 'b'}
        },
        {
            data: {id: 'ab', source: 'a', target: 'b'}
        }
    ],
    style: [ // the stylesheet for the graph
        {
            selector: 'node',
            style: {
                'background-color': '#666',
                'label': 'data(id)'
            }
        },
        {
            selector: 'edge',
            style: {
                'width': 3,
                'line-color': '#ccc',
                'target-arrow-color': '#ccc',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier'
            }
        }
      ],
    layout: {
        name: 'grid',
        rows: 1
    }
});
