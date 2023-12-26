import {Network} from "vis-network";


const visData = JSON.parse(document.getElementById("vis-data")!.textContent!);
console.log(visData);
const container = document.getElementById("vis-container");
const options = {
    layout: {
        improvedLayout: false,
    },
    nodes: {
        font: {
            size: 24,
        },
        opacity: 0.8,
        shape: "box",
    },
    edges: {
        smooth: false,
    },
    physics: {
        barnesHut: {
            gravitationalConstant: -10000,
            springLength: 200,
        },
    }
};

new Network(container!, visData, options);
