MAE259B.setTc = (el, content) => el.replaceChild(document.createTextNode(content), el.firstChild);

MAE259B.setUpAnimOptions = () => {
    const el$exaggerate = document.getElementById('animopt-exaggerate');
    const el$speed = document.getElementById('animopt-speed');
    const el$showpoints = document.getElementById('animopt-showpoints');
    const el$screenshotIndicator = document.getElementById('animopt-screenshot-indicator');
    const el$screenshot = document.getElementById('animopt-screenshot-interval');
    const map = input => Math.round(Math.exp(input.value * Math.log(100)) * 1000) / 1000;
    [el$exaggerate, el$speed].forEach(input => input.addEventListener('input', () =>
        MAE259B.setTc(input.parentNode.nextElementSibling, map(input))
    ));
    el$screenshot.addEventListener('input', () => {
        const val = parseFloat(el$screenshot.value);
        if (isNaN(val) || (val <= 0)) {
            MAE259B.setTc(el$screenshotIndicator, 'off');
            el$screenshotIndicator.className = 'badge badge-light';
        } else {
            MAE259B.setTc(el$screenshotIndicator, 'on');
            el$screenshotIndicator.className = 'badge badge-primary';
        }
    });
    return () => ({
        exaggerateY: map(el$exaggerate),
        speed: map(el$speed),
        showNodes: el$showpoints.checked,
        screenshotEvery: Math.max(parseFloat(el$screenshot.value) || 0, 0)
    });
};