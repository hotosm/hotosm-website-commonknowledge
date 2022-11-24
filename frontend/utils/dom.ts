export function createElement(
    html: string,
    element: string = "div",
    root = document,
) {
    const el = root.createElement(element);
    document.body.appendChild(el);
    el.innerHTML = html;
    return el;
}
