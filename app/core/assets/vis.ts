import {Network} from "vis-network";


const defaultOptions = {
    layout: {
        improvedLayout: false,
    },
    nodes: {
        font: {
            size: 20,
        },
        opacity: 0.8,
        shape: "dot",
    },
    edges: {
        smooth: false,
    },
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
