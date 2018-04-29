MAE259B.render = ({ meta, frames }, options, { saveScreenshot, el$canvas, el$display }) => {
    const QUALITY_FACTOR = 1; // might be an INTERGER larger than 1, for adding intermediate nodes for rendering, use Catmull-Rom interpolation
    const USE_IMAGE = true; // true to use image for the ground-plane, instead of solid color

    const destWidth = el$canvas.parentNode.clientWidth;
    const destHeight = el$canvas.parentNode.clientHeight - el$canvas.previousElementSibling.clientHeight;
    el$canvas.width = destWidth;
    el$canvas.height = destHeight;
    el$canvas.style.display = 'block';

    let minX = Number.MAX_VALUE;
    let maxX = Number.MIN_VALUE;
    let minY = Number.MAX_VALUE;
    let maxY = Number.MIN_VALUE;

    frames.forEach(row => row.points.forEach(entry => {
        if (entry.x > maxX) { maxX = entry.x; }
        if (entry.x < minX) { minX = entry.x; }
        if (entry.y > maxY) { maxY = entry.y; }
        if (entry.y < minY) { minY = entry.y; }
    }));
    const path = new THREE.CatmullRomCurve3(frames[0].points, meta.closed);
    const sections = (frames[0].points.length - (meta.closed ? 0 : 1)) * QUALITY_FACTOR;

    const geometry = new THREE.TubeBufferGeometry(path, sections, meta.radius, options.showNodes ? 16 : 32, meta.closed);

    const material = new THREE.MeshLambertMaterial({
        color: 0x2962FF,
        wireframe: options.showNodes
    });

    const scene = new THREE.Scene();
    scene.add(new THREE.Mesh(geometry, material));
    scene.add(new THREE.AmbientLight(0xffffff, 1));
    scene.add(new THREE.DirectionalLight(0xffff00, 2));
    // const thirdLight = new THREE.PointLight(0xffff00, 1);
    // thirdLight.position.set((minX + maxX) / 2, maxY + (maxY - minY) * 0.25, 0);
    // thirdLight.lookAt((minX + maxX) / 2, minY, 0);
    // scene.add(thirdLight);

    const dotGeometry = options.showNodes ? new THREE.Geometry() : null;
    if (options.showNodes) {
        frames[0].points.forEach(entry =>
            dotGeometry.vertices.push(new THREE.Vector3(entry.x, entry.y, 0))
        );
        const dotMaterial = new THREE.PointsMaterial({ size: 4, sizeAttenuation: false, color: 0xffffff });
        scene.add(new THREE.Points(dotGeometry, dotMaterial));
    }

    if (meta.ground) {
        const texture = new THREE.TextureLoader().load('static/book.jpg');
        texture.anisotropy = 32;
        const gndMaterial = USE_IMAGE ? new THREE.MeshBasicMaterial({ map: texture }) :  new THREE.MeshLambertMaterial({ color: 0x333366 });
        const gndGeometry = new THREE.PlaneGeometry((maxX - minX) * 1.5, (maxX - minX) * 1.5 * 1373 / 2082);
        const gndPlane = new THREE.Mesh(gndGeometry, gndMaterial);
        gndPlane.position.set((minX + maxX) / 2, - meta.radius, 0);
        gndPlane.lookAt(new THREE.Vector3((minX + maxX) / 2, 1, 0));
        scene.add(gndPlane);
    }

    const cameraZ4Y = (maxY - minY + 4 * meta.radius) / 1.75 / Math.tan(Math.PI * 45 / 360); // https://stackoverflow.com/a/23361117/2098471
    const cameraZ4X = ((maxX - minX + 4 * meta.radius) * destHeight / destWidth) / 1.75 / Math.tan(Math.PI * 45 / 360);
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, Math.max(cameraZ4X, cameraZ4Y) / 4, 500);
    camera.position.set((minX + maxX) / 2, (minY + maxY) / 2, Math.max(cameraZ4X, cameraZ4Y));
    camera.lookAt(new THREE.Vector3((minX + maxX) / 2, (minY + maxY) / 2, 0));

    const renderer = new THREE.WebGLRenderer({ canvas: el$canvas, antialias: true });
    renderer.render(scene, camera);

    let startTime = null;
    let fIndexHigh = 1;
    const doAnimation = secondsElapsed => {
        let shouldRequestNextFrame = true;
        while (frames[fIndexHigh].time < secondsElapsed) {
            if (fIndexHigh === frames.length - 1) {
                // final state reached
                secondsElapsed = frames[fIndexHigh].time;
                shouldRequestNextFrame = false;
                break;
            }
            fIndexHigh++;
        }
        const fIndexLow = fIndexHigh - 1;
        const frameIndex = (secondsElapsed - frames[fIndexLow].time) / (frames[fIndexHigh].time - frames[fIndexLow].time) + fIndexLow;
        const nodes = frames[fIndexHigh].points.map((fhp, vindex) => {
            return new THREE.Vector3(
                fhp.x * (frameIndex - fIndexLow) + frames[fIndexLow].points[vindex].x * (fIndexHigh - frameIndex),
                fhp.y * (frameIndex - fIndexLow) + frames[fIndexLow].points[vindex].y * (fIndexHigh - frameIndex),
                fhp.z * (frameIndex - fIndexLow) + frames[fIndexLow].points[vindex].z * (fIndexHigh - frameIndex)
            );
        });
        if (options.showNodes) {
            nodes.forEach((node, vindex) => {
                dotGeometry.vertices[vindex].set(node.x, node.y, node.z);
            });
            dotGeometry.verticesNeedUpdate = true;
        }
        geometry.copy(new THREE.TubeBufferGeometry(new THREE.CatmullRomCurve3(nodes, meta.closed), sections, meta.radius, options.showNodes ? 16 : 32, meta.closed));
        geometry.needUpdate = true;
        MAE259B.setTc(el$display, 'Animating: t = ' + secondsElapsed.toFixed(3));
        renderer.render(scene, camera);
        return shouldRequestNextFrame;
    };
    const animate = function (time) {
        if (!startTime) {
            startTime = time;
            requestAnimationFrame(animate);
            return;
        }
        let secondsElapsed = (time - startTime) / 1000 * options.speed;
        if (doAnimation(secondsElapsed)) {
            requestAnimationFrame(animate);
        }
    };
    if (options.screenshotEvery) { // screenshot mode
        let currentTime = 0;
        const step = () => {
            saveScreenshot(currentTime).then(() => {
                currentTime += options.screenshotEvery;
                if (doAnimation(currentTime)) {
                    step();
                }
            });
        };
        step();
    } else { // animate mode
        requestAnimationFrame(animate);
    }
};