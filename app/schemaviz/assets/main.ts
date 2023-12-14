import {Network, Options} from "vis-network";

const context_data = JSON.parse(document.getElementById("vis-data")!.textContent!);
let container = document.getElementById("vis-container");
let data = context_data;
let options: Options = {
    nodes: {
        font: {
            size: 20
        },
        opacity: 0.8,
        shape: 'dot',
    },
    edges: {
        arrows: {
            to: {
                enabled: true
            }
        },
        color: {
            opacity: 0.5
        },
        // physics: false,
        // smooth: {
            // enabled: false,  // true
            // type: 'dynamic',  // dynamic
        // }
    },
    physics: {
        barnesHut: {
            gravitationalConstant: -2000,  // -2000
            damping: 0.5,  // 0.09
            springLength: 100,  // 95
            springConstant: 0.02,  // 0.04
            avoidOverlap: 0.1,  // 0
        },
        repulsion: {
            nodeDistance: 200,  // 100
            damping: 0.5,  // 0.09
        },
        // solver: 'repulsion'  // 'barnesHut'
    }
};
new Network(container!, data, options);
