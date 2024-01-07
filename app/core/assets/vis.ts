import {Network} from "vis-network";


const defaultOptions = {
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


const visData = JSON.parse(document.getElementById("vis-data")!.textContent!);
let visOptions;
let element = document.getElementById("vis-options");
if (element !== null) {
    visOptions = JSON.parse(element.textContent!);
}
else {
    visOptions = defaultOptions;
}

console.log(visData);
console.log(visOptions);

const container = document.getElementById("vis-container");
new Network(container!, visData, visOptions);
