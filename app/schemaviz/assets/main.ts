import {Network, Options} from "vis-network";

const context_data = JSON.parse(document.getElementById("vis-data")!.textContent!);
let container = document.getElementById("vis-container");
let data = context_data;
let options: Options = {
    nodes: {
        font: {
            size: 20
        },
        mass: 1,
        opacity: 0.8,
        shape: 'dot',
        value: 1,
    },
    edges: {
        arrows: {
            to: {
                enabled: true
            }
        },
    },
};
new Network(container!, data, options);
