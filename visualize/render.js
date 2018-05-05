MAE259B.render = ({ meta, frames }, options, { saveScreenshot, el$canvas, el$display, buttons }) => {
    const QUALITY_FACTOR = 2; // might be an INTERGER larger than 1, for adding intermediate nodes for rendering, use Catmull-Rom interpolation
    const USE_IMAGE_FOR_GROUND = false; // true to use image for the ground-plane, instead of solid color
    const USE_IMAGE_FOR_RING = true; // true to use image for the ground-plane, instead of solid color

    // start loading the texture images first, if needed
    const rodMaterialConfig = USE_IMAGE_FOR_RING ? MAE259B.loadTexture('static/two.png').then(rodTexture => {
        rodTexture.rotation = meta.closed ? 0 : Math.PI / 2;
        return { map: rodTexture };
    }) : Promise.resolve({ color: 0x2962FF });
    const groundMaterialConfig = meta.ground ? (USE_IMAGE_FOR_GROUND ? MAE259B.loadTexture('static/book.png').then(texture => {
        texture.anisotropy = 32;
        return { map: rodTexture };
    }) : Promise.resolve({ color: 0xCCCC66 })) : Promise.resolve(null);

    const destWidth = el$canvas.parentNode.clientWidth;
    const destHeight = el$canvas.parentNode.clientHeight - el$canvas.previousElementSibling.clientHeight;
    el$canvas.width = destWidth;
    el$canvas.height = destHeight;
    el$canvas.style.display = 'block';

    const scene = new THREE.Scene();
    scene.add(new THREE.AmbientLight(0xffffff, 1));
    scene.add(new THREE.DirectionalLight(0xffff99, 2));

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

    // configure the camera
    const cameraZ4Y = (maxY - minY + 4 * meta.radius) / 1.75 / Math.tan(Math.PI * 45 / 360); // https://stackoverflow.com/a/23361117/2098471
    const cameraZ4X = ((maxX - minX + 4 * meta.radius) * destHeight / destWidth) / 1.75 / Math.tan(Math.PI * 45 / 360);
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, Math.max(cameraZ4X, cameraZ4Y) / 4, 500);
    const baseCameraPosition = new THREE.Vector3((minX + maxX) / 2, (minY + maxY) / 2, Math.max(cameraZ4X, cameraZ4Y));
    camera.position.set(baseCameraPosition.x, baseCameraPosition.y, baseCameraPosition.z);

    // orbit controls of the camera
    const controls = new THREE.OrbitControls(camera, el$canvas);
    controls.target = new THREE.Vector3(baseCameraPosition.x, baseCameraPosition.y, 0);
    controls.saveState();
    controls.update();

    Promise.all([rodMaterialConfig, groundMaterialConfig]).then(([rodMaterialParameter, groundMaterialParameter]) => {
        // everything's ready. start creating actual meshes

        // mesh: rod itself
        const sections = (frames[0].points.length - (meta.closed ? 0 : 1)) * QUALITY_FACTOR;
        const rodGeometry = new THREE.TubeBufferGeometry(path, sections, meta.radius, options.showNodes ? 12 : 24, meta.closed);
        const rodMaterial = new THREE.MeshLambertMaterial(Object.assign(rodMaterialParameter, {
            wireframe: options.showNodes,
            opacity: options.showNodes ? 0.5 : 1,
            transparent: options.showNodes
        }));
        scene.add(new THREE.Mesh(rodGeometry, rodMaterial));

        // mesh: nodes (if showNodes is enabled)
        const dotGeometry = options.showNodes ? new THREE.Geometry() : null;
        if (options.showNodes) {
            frames[0].points.forEach(entry =>
                dotGeometry.vertices.push(new THREE.Vector3(entry.x, entry.y, 0))
            );
            const dotMaterial = new THREE.PointsMaterial({ size: 8, sizeAttenuation: false, color: 0xffffff });
            scene.add(new THREE.Points(dotGeometry, dotMaterial));
        }

        // mesh: ground (if ground is enabled)
        if (meta.ground) {
            const gndGeometry = new THREE.PlaneGeometry((maxX - minX) * 1.5, (maxX - minX) * 1.5 * 1373 / 2082);
            const gndPlane = new THREE.Mesh(gndGeometry, new THREE.MeshBasicMaterial(groundMaterialParameter));
            gndPlane.material.side = THREE.DoubleSide;
            gndPlane.position.set((minX + maxX) / 2, - meta.radius, 0);
            gndPlane.lookAt(new THREE.Vector3((minX + maxX) / 2, 1, 0));
            scene.add(gndPlane);
        }

        // initiate the renderer
        const renderer = new THREE.WebGLRenderer({ canvas: el$canvas, antialias: true });
        renderer.autoClear = false;

        const dtIndicator = options.showDt ? MAE259B.dtIndicator(frames) : null;

        // animation loop
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
            const nodes = frames[fIndexHigh].points.map((fhp, vindex) => new THREE.Vector3(
                fhp.x * (frameIndex - fIndexLow) + frames[fIndexLow].points[vindex].x * (fIndexHigh - frameIndex),
                fhp.y * (frameIndex - fIndexLow) + frames[fIndexLow].points[vindex].y * (fIndexHigh - frameIndex),
                fhp.z * (frameIndex - fIndexLow) + frames[fIndexLow].points[vindex].z * (fIndexHigh - frameIndex)
            ));
            if (options.showNodes) {
                nodes.forEach((node, vindex) => {
                    dotGeometry.vertices[vindex].set(node.x, node.y, node.z);
                });
                dotGeometry.verticesNeedUpdate = true;
            }
            rodGeometry.copy(new THREE.TubeBufferGeometry(new THREE.CatmullRomCurve3(nodes, meta.closed), sections, meta.radius, options.showNodes ? 12 : 24, meta.closed));
            rodGeometry.needUpdate = true;

            MAE259B.setTc(el$display, 'Animating: t = ' + secondsElapsed.toFixed(3));
            renderer.clear();
            renderer.render(scene, camera);
            if (options.showDt) {
                renderer.clearDepth();
                dtIndicator.setFrameNumber(fIndexHigh);
                renderer.render(dtIndicator.scene, dtIndicator.camera);
            }
            return shouldRequestNextFrame;
        };
        doAnimation(0); // initial render

        if (options.screenshotEvery) { // screenshot mode
            let currentTime = 0;
            const step = () => {
                const fin = doAnimation(currentTime);
                saveScreenshot(currentTime).then(() => {
                    if (fin) {
                        currentTime += options.screenshotEvery;
                        step();
                    } else {
                        window.alert('Finished. View screenshots directory for results.');
                    }
                });
            };
            step();
        } else { // animate mode
            document.body.classList.remove('not-playing');
            let animationActive = true;
            let startTime = null;
            const animate = time => {
                if (!startTime) {
                    startTime = time; // must render t = 0 again
                }
                let secondsElapsed;
                if (animationActive) {
                    secondsElapsed = (time - startTime) / 1000 * options.speed;
                } else {
                    secondsElapsed = frames[fIndexHigh].time;
                }
                if (!doAnimation(secondsElapsed)) { // loop again
                    startTime = null;
                    fIndexHigh = 1;
                }
                requestAnimationFrame(animate);
            };
            buttons.backward.addEventListener('click', () => {
                animationActive = false;
                fIndexHigh -= 1;
            });
            buttons.forward.addEventListener('click', () => {
                animationActive = false;
                fIndexHigh += 1;
            });
            buttons.play.addEventListener('click', () => {
                if (animationActive) { return; }
                startTime = performance.now() - frames[fIndexHigh].time * 1000 / options.speed;
                animationActive = true;
            });
            buttons.reset.addEventListener('click', () => {
                controls.reset();
            });
            requestAnimationFrame(animate);
        }
    });
};