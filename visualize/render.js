MAE259B.render = ({ meta, frames }, options, { saveScreenshot, el$canvas, el$display, buttons }) => {
    const QUALITY_FACTOR = 2; // might be an INTERGER larger than 1, for adding intermediate nodes for rendering, use Catmull-Rom interpolation

    MAE259B.setTc(el$display, 'Animating: t = 0.000');

    // start loading the texture images first, if needed
    const rodTexture = MAE259B.loadTexture('visualize/two.png');
    const groundMaterialConfig = meta.ground ? (options.noBook ? Promise.resolve({ color: 0xCCCC66 }) : MAE259B.loadTexture('visualize/book.jpg').then(texture => {
        texture.anisotropy = 32;
        return { map: texture };
    })) : Promise.resolve(null);

    const destWidth = el$canvas.parentNode.clientWidth;
    const destHeight = el$canvas.parentNode.clientHeight - el$canvas.previousElementSibling.clientHeight;
    el$canvas.width = destWidth;
    el$canvas.height = destHeight;
    el$canvas.style.display = 'block';

    const scene = new THREE.Scene();

    let minX = Number.POSITIVE_INFINITY;
    let maxX = Number.NEGATIVE_INFINITY;
    let minY = Number.POSITIVE_INFINITY;
    let maxY = Number.NEGATIVE_INFINITY;
    let maxWidth = 0;
    let maxHeight = 0;
    frames.forEach(row => {
        let frameMinX = Number.POSITIVE_INFINITY;
        let frameMaxX = Number.NEGATIVE_INFINITY;
        let frameMinY = Number.POSITIVE_INFINITY;
        let frameMaxY = Number.NEGATIVE_INFINITY;
        row.structures.forEach(structure => {
            structure.forEach(entry => {
                if (entry.x < frameMinX) { frameMinX = entry.x; }
                if (entry.x > frameMaxX) { frameMaxX = entry.x; }
                if (entry.y < frameMinY) { frameMinY = entry.y; }
                if (entry.y > frameMaxY) { frameMaxY = entry.y; }
            });
        });
        if (frameMinX < minX) { minX = frameMinX; }
        if (frameMaxX > maxX) { maxX = frameMaxX; }
        if (frameMinY < minY) { minY = frameMinY; }
        if (frameMaxY > maxY) { maxY = frameMaxY; }
        const width = frameMaxX - frameMinX;
        const height = frameMaxY - frameMinY;
        if (width > maxWidth) {
            maxWidth = width;
        }
        if (height > maxHeight) { maxHeight = height; }
    });
    const pathes = frames[0].structures.map(structure => new THREE.CatmullRomCurve3(structure, meta.closed));

    // configure the camera
    const cameraZ4Y = ((options.vpTrack ? maxHeight : (maxY - minY)) + 4 * meta.radius) / 1.75 / Math.tan(Math.PI * 45 / 360); // https://stackoverflow.com/a/23361117/2098471
    const cameraZ4X = (((options.vpTrack ? maxWidth : (maxX - minX)) + 4 * meta.radius) * destHeight / destWidth) / 1.75 / Math.tan(Math.PI * 45 / 360);
    const baseZ = Math.max(cameraZ4X, cameraZ4Y);
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, baseZ / 1000, baseZ * 2000);
    camera.position.set((minX + maxX) / 2, (minY + maxY) / 2, baseZ);

    // orbit controls of the camera
    let controls = null;
    if (!options.vpTrack) {
        controls = new THREE.OrbitControls(camera, el$canvas);
        controls.target = new THREE.Vector3((minX + maxX) / 2, (minY + maxY) / 2, 0);
        controls.saveState();
        controls.update();
    }

    // configure lights
    scene.add(new THREE.AmbientLight(0xccccff, 0.75));
    const pointLight = new THREE.PointLight(0xffff99, 0.75);
    pointLight.position.set((minX + maxX) / 2, maxY + meta.radius + maxY - minY, 0);
    if (options.shadow) {
        pointLight.castShadow = true;
        pointLight.shadow.mapSize.width = 1024;
        pointLight.shadow.mapSize.height = 2048;
        pointLight.shadow.camera.near = baseZ / 1000;
        pointLight.shadow.camera.far = baseZ * 2000;
    }
    scene.add(pointLight);

    Promise.all([rodTexture, groundMaterialConfig]).then(([rodMaterialTexture, groundMaterialParameter]) => {
        // everything's ready. start creating actual meshes
        const rodMaterial = new THREE.MeshLambertMaterial({
            map: rodMaterialTexture,
            wireframe: options.showNodes,
            opacity: options.showNodes ? 0.5 : 1,
            transparent: options.showNodes
        });
        rodMaterial.emissive = new THREE.Color(0xffffff);
        rodMaterial.emissiveMap = rodMaterialTexture;
        rodMaterial.emissiveIntensity = 0.25;
        const rodGeometries = pathes.map((path, structureId) => {
            // mesh: rod itself
            const sections = (frames[0].structures[structureId].length - (meta.closed ? 0 : 1)) * QUALITY_FACTOR;
            const rodGeometry = new THREE.TubeBufferGeometry(path, sections, meta.radius, options.showNodes ? 12 : 24, meta.closed);
            const rod = new THREE.Mesh(rodGeometry, rodMaterial);
            rod.castShadow = options.shadow;
            scene.add(rod);
            return { sections, rodGeometry };
        });
        const dotGeometries = options.showNodes ? frames[0].structures.map(structure => {
            // mesh: nodes (if showNodes is enabled)
            const dotGeometry =new THREE.Geometry();
            structure.forEach(entry =>
                dotGeometry.vertices.push(new THREE.Vector3(entry.x, entry.y, 0))
            );
            const dotMaterial = new THREE.PointsMaterial({ size: 8, sizeAttenuation: false, color: 0xffffff });
            scene.add(new THREE.Points(dotGeometry, dotMaterial));
            return dotGeometry;
        }) : null;

        // mesh: ground (if ground is enabled)
        if (meta.ground) {
            const groundAngle = (meta.groundAngle || 0) * Math.PI / 180;
            const gndGeometry = new THREE.PlaneGeometry((maxX - minX) * 1.5, (maxX - minX) * 1.5 * 1373 / 2082);
            const gndMaterial = new THREE.MeshLambertMaterial(Object.assign({}, groundMaterialParameter));
            gndMaterial.side = THREE.DoubleSide;
            const gndPlane = new THREE.Mesh(gndGeometry, gndMaterial);
            gndPlane.receiveShadow = options.shadow;
            const correspondingY = Math.tan(groundAngle) * (minX + maxX) / 2 - meta.radius / Math.cos(groundAngle);
            gndPlane.position.set((minX + maxX) / 2, correspondingY, 0);
            gndPlane.lookAt(new THREE.Vector3((minX + maxX) / 2 - Math.sin(groundAngle), correspondingY + Math.cos(groundAngle), 0));
            if (meta.groundAngle !== 90) {
                gndPlane.rotateZ(Math.PI / 2)
            }
            scene.add(gndPlane);
        }

        // initiate the renderer
        const renderer = new THREE.WebGLRenderer({ canvas: el$canvas, antialias: true });
        if (options.shadow) {
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap; // default THREE.PCFShadowMap
        }
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

            let xC = 0;
            let yC = 0;
            let nC = 0;
            rodGeometries.forEach(({ sections, rodGeometry }, structureId) => {
                const nodes = frames[fIndexHigh].structures[structureId].map((fhp, vindex) => new THREE.Vector3(
                    fhp.x * (frameIndex - fIndexLow) + frames[fIndexLow].structures[structureId][vindex].x * (fIndexHigh - frameIndex),
                    fhp.y * (frameIndex - fIndexLow) + frames[fIndexLow].structures[structureId][vindex].y * (fIndexHigh - frameIndex),
                    fhp.z * (frameIndex - fIndexLow) + frames[fIndexLow].structures[structureId][vindex].z * (fIndexHigh - frameIndex)
                ));
                if (options.showNodes) {
                    nodes.forEach((node, vindex) => {
                        dotGeometries[structureId].vertices[vindex].set(node.x, node.y, node.z);
                    });
                    dotGeometries[structureId].verticesNeedUpdate = true;
                }
                rodGeometry.copy(new THREE.TubeBufferGeometry(new THREE.CatmullRomCurve3(nodes, meta.closed), sections, meta.radius, options.showNodes ? 12 : 24, meta.closed));
                rodGeometry.needUpdate = true;
                if (options.vpTrack) {
                    nodes.forEach(node => { xC += node.x; yC += node.y; });
                    nC += nodes.length;
                }
            });
            if (options.vpTrack) {
                xC /= nC; yC /= nC;
                camera.position.set(xC, yC, baseZ);
                camera.lookAt(xC, yC, 0);
            }
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
                if (controls) {
                    controls.reset();
                } else {
                    window.alert('Camera cannot be adjusted when viewport tracking is on.');
                }
            });
            requestAnimationFrame(animate);
        }
    });
};