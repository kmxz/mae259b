MAE259B.setTc = (el, content) => el.replaceChild(document.createTextNode(content), el.firstChild);

MAE259B.setUpAnimOptions = () => {
    const el$exaggerate = document.getElementById('animopt-exaggerate');
    const el$speed = document.getElementById('animopt-speed');
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
        showNodes: document.getElementById('animopt-showpoints').checked,
        showDt: document.getElementById('animopt-showdt').checked,
        shadow: document.getElementById('animopt-shadow').checked,
        noBook: document.getElementById('animopt-nobook').checked,
        vpTrack: document.getElementById('animopt-track').checked,
        screenshotEvery: Math.max(parseFloat(el$screenshot.value) || 0, 0)
    });
};

MAE259B.dtIndicator = frames => {
    const RECIPPROCAL_SIZE_OF_INDICATOR = 4; // larger number for smaller size

    const maxTime = frames[frames.length - 1].time;

    const positions = new Float32Array(frames.length * 3);

    let maxDt = 0;
    for (let i = 1; i < frames.length; i++) {
        const dt = frames[i].time - frames[i - 1].time;
        if (dt > maxDt) { maxDt = dt; }
        positions[3 * i] = frames[i].time / maxTime;
        positions[3 * i + 1] = dt;
    }
    positions[0] = positions[3]; // fake t=0 data (x)
    positions[1] = positions[4]; // fake t=0 data (y)

    const geometry = new THREE.BufferGeometry();
    geometry.addAttribute('position', new THREE.BufferAttribute(positions, 3));
    const line = new THREE.Line(geometry, new THREE.LineBasicMaterial({
        color: 0xffffff
    }));

    const camera = new THREE.OrthographicCamera(-0.5, 0.5, maxDt * 1.1, -RECIPPROCAL_SIZE_OF_INDICATOR * maxDt, 1, 4);
    camera.position.set(0.5, 0, 2);
    camera.lookAt(new THREE.Vector3(0.5, 0, 0));

    const gndGeometry = new THREE.PlaneGeometry(1, maxDt * 1.2);
    const gndPlane = new THREE.Mesh(gndGeometry, new THREE.MeshBasicMaterial({ color: 0x2780E3, opacity: 0.5, transparent: true }));
    gndPlane.position.set(0.5, maxDt * 0.5, -1);
    gndPlane.lookAt(0.5, maxDt * 0.5, 1);

    const scene = new THREE.Scene();
    scene.add(line);
    scene.add(camera);
    scene.add(gndPlane);

    return { scene, camera, setFrameNumber: (i => geometry.setDrawRange(0, i)) };
};

MAE259B.loadTexture = file => new Promise((res, rej) => new THREE.TextureLoader().load(file, res, null, rej));