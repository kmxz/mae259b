MAE259B.render = ({ meta, frames }, options, { saveScreenshot, el$canvas, el$display, el$resetBtn }) => {
    const QUALITY_FACTOR = 1; // might be an INTERGER larger than 1, for adding intermediate nodes for rendering, use Catmull-Rom interpolation
    const USE_IMAGE_FOR_GROUND = false; // true to use image for the ground-plane, instead of solid color
    const USE_IMAGE_FOR_RING = false; // true to use image for the ground-plane, instead of solid color

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

    const geometry = new THREE.TubeBufferGeometry(path, sections, meta.radius, options.showNodes ? 12 : 24, meta.closed);

    const rodTexture = new THREE.TextureLoader().load('static/two.png');
    rodTexture.rotation = meta.closed ? 0 : Math.PI / 2;
    const material = new THREE.MeshLambertMaterial(Object.assign(USE_IMAGE_FOR_RING ? { map: rodTexture } : { color: 0x2962FF }, {
        wireframe: options.showNodes,
        opacity: options.showNodes ? 0.25 : 1
    }));

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
        const dotMaterial = new THREE.PointsMaterial({ size: 8, sizeAttenuation: false, color: 0xffffff });
        scene.add(new THREE.Points(dotGeometry, dotMaterial));
    }

    if (meta.ground) {
        const texture = new THREE.TextureLoader().load('static/book.jpg');
        texture.anisotropy = 32;
        const gndMaterial = USE_IMAGE_FOR_GROUND ? new THREE.MeshBasicMaterial({ map: texture }) :  new THREE.MeshLambertMaterial({ color: 0x333366 });
        const gndGeometry = new THREE.PlaneGeometry((maxX - minX) * 1.5, (maxX - minX) * 1.5 * 1373 / 2082);
        const gndPlane = new THREE.Mesh(gndGeometry, gndMaterial);
        gndPlane.material.side = THREE.DoubleSide;
        gndPlane.position.set((minX + maxX) / 2, - meta.radius, 0);
        gndPlane.lookAt(new THREE.Vector3((minX + maxX) / 2, 1, 0));
        scene.add(gndPlane);
    }

    const cameraRotator = MAE259B.initCamera(el$canvas, el$resetBtn);
    const cameraZ4Y = (maxY - minY + 4 * meta.radius) / 1.75 / Math.tan(Math.PI * 45 / 360); // https://stackoverflow.com/a/23361117/2098471
    const cameraZ4X = ((maxX - minX + 4 * meta.radius) * destHeight / destWidth) / 1.75 / Math.tan(Math.PI * 45 / 360);
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, Math.max(cameraZ4X, cameraZ4Y) / 4, 500);
    const baseCameraPosition = new THREE.Vector3((minX + maxX) / 2, (minY + maxY) / 2, Math.max(cameraZ4X, cameraZ4Y));
    camera.position.set(baseCameraPosition.x, baseCameraPosition.y, baseCameraPosition.z);
    camera.lookAt(new THREE.Vector3(baseCameraPosition.x, baseCameraPosition.y, 0));

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
        geometry.copy(new THREE.TubeBufferGeometry(new THREE.CatmullRomCurve3(nodes, meta.closed), sections, meta.radius, options.showNodes ? 12 : 24, meta.closed));
        geometry.needUpdate = true;

        camera.position.set(Math.sin(cameraRotator.h) * baseCameraPosition.z + baseCameraPosition.x, Math.sin(cameraRotator.v) * baseCameraPosition.z + baseCameraPosition.y, Math.cos(cameraRotator.h) * baseCameraPosition.z);
        camera.lookAt(new THREE.Vector3(baseCameraPosition.x, baseCameraPosition.y, 0));

        MAE259B.setTc(el$display, 'Animating: t = ' + secondsElapsed.toFixed(3));
        renderer.render(scene, camera);
        return shouldRequestNextFrame;
    };
    const animate = function (time) {
        if (!startTime) {
            startTime = time;
        } else {
            let secondsElapsed = (time - startTime) / 1000 * options.speed;
            if (!doAnimation(secondsElapsed)) { // loop again
                startTime = time;
                fIndexHigh = 1;
            }
        }
        requestAnimationFrame(animate);
    };
    if (options.screenshotEvery) { // screenshot mode
        let currentTime = 0;
        const step = () => {
            saveScreenshot(currentTime).then(() => {
                currentTime += options.screenshotEvery;
                if (doAnimation(currentTime)) {
                    step();
                } else {
                    window.alert('Finished. View screenshots directory for results.');
                }
            });
        };
        step();
    } else { // animate mode
        requestAnimationFrame(animate);
    }
};