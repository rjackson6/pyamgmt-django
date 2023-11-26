import {Network} from "vis-network";


const context_data = JSON.parse(document.getElementById("vis-data")!.textContent!);
const nodes = JSON.parse(document.getElementById("nodes")!.textContent!);
const edges = JSON.parse(document.getElementById("edges")!.textContent!);
console.debug(context_data);
let container = document.getElementById("vis-container");
let data = {
    nodes: nodes,
    edges: edges,
}
new Network(container!, data, {});
