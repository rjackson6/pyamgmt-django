import { createSignal, createEffect } from 'solid-js';

const [currentDate, setDate] = createSignal(new Date());

const elms = document.getElementsByClassName('js-header-clock')
const elm = elms[0];

createEffect(() => {
    elm.textContent = currentDate().toLocaleTimeString();
});

setInterval(() => {
    setDate(new Date());
}, 1000);
