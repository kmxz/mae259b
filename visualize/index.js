const MAE259B = {};

MAE259B.init = () => {
    if (window.location.port !== '') {
        document.body.classList.remove('guest');
        document.body.classList.add('non-guest');
    }

    const el$welcome = document.getElementById('welcome');
    const el$display = document.getElementById('display');
    const el$title = document.getElementById('title');
    const el$canvas = document.getElementById('canvas');
    const el$codePreviewRow = document.getElementById('code-preview-row');
    const el$codePreview = document.getElementById('code-preview');
    const el$fileName = document.getElementById('file-name');
    const animOptions = MAE259B.setUpAnimOptions();

    let currentId = null;
    const saveScreenshot = time => new Promise((res, rej) =>
        el$canvas.toBlob(blob => {
            const fd = new FormData();
            fd.append('id', currentId);
            fd.append('time', time.toFixed(3));
            fd.append('image', blob);
            fetch('save', {
                method: 'POST',
                body: fd
            }).then(response => response.text()).then(res).catch(rej);
        })
    );

    let jsonData = null;

    fetch('list').then(response => response.json()).then(dirs => {
        const keys = Object.keys(dirs).sort();
        if (keys.length) {
            let selected = null;
            const fl = document.getElementById('file-list');
            const btn = document.getElementById('start-button');
            MAE259B.setTc(fl.previousElementSibling, 'Select a previous result to load.');
            btn.classList.remove('disabled');
            keys.forEach(dir => {
                let parent;
                if (dir) {
                    parent = document.createElement('li');
                    parent.className = 'list-group-item py-2';
                    const iconClose = document.createElement('i');
                    iconClose.className = 'material-icons mr-1 folder-icon';
                    parent.appendChild(iconClose);
                    parent.appendChild(document.createTextNode(dir.replace(/^\/+/, '')));
                    fl.appendChild(parent);
                }
                const lis = dirs[dir].map(entry => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item pl-5 py-2';
                    li.appendChild(document.createTextNode(entry));
                    li.addEventListener('click', () => {
                        if (selected) { selected.classList.remove('active'); }
                        selected = li;
                        li.classList.add('active');
                        el$codePreviewRow.style.display = 'none';
                        jsonData = fetch('data' + dir + '/' + entry + '?at=' + Date.now()).then(response => response.json());
                        jsonData.then(data => {
                            if (data.code) {
                                MAE259B.setTc(el$fileName, entry);
                                MAE259B.setTc(el$codePreview, data.code);
                                el$codePreviewRow.style.display = 'block';
                            }
                        });
                    });
                    fl.appendChild(li);
                    return li;
                });
                if (parent) {
                    lis.forEach(li => li.style.display = 'none');
                    parent.addEventListener('click', () => {
                        const now = parent.classList.contains('text-muted');
                        lis.forEach(now ? (li => li.style.display = 'none') : (li => li.style.display = 'block'));
                        parent.classList[now ? 'remove' : 'add']('text-muted');
                    });
                }
            });
            fl.style.display = 'block';
            btn.addEventListener('click', () => {
                if (!selected) {
                    window.alert('Please select a file first!');
                } else {
                    const title = selected.firstChild.textContent;
                    const options = animOptions();
                    if (options.screenshotEvery) {
                        currentId = title.substr(0, title.length - 4).replace(/[^A-Za-z0-9_]/g, '').substr(0, 4);
                        while (currentId.length < 5) {
                            currentId += String.fromCharCode(Math.random() * 26 + 97);
                        }
                        window.alert('Screenshot will be save with a prefix of ' + currentId + ',');
                    }
                    jsonData.then(data => {
                        const nos = data.meta.numberOfStructure;
                        data.frames.forEach(frame => {
                            frame.structures = (nos ? frame.data : [frame.data]).map(input => {
                                let output = [];
                                for (let i = 0; i < input.length; i += 2) {
                                    output.push(new THREE.Vector3(input[i], input[i + 1] * options.exaggerateY, 0));
                                }
                                return output;
                            });
                            delete frame.data;
                        });

                        MAE259B.setTc(el$title, title);
                        el$welcome.style.display = 'none';
                        const buttons = {};
                        ['backward', 'forward', 'play', 'reset', 'close'].forEach(name => {
                            buttons[name] = document.getElementById(name + '-btn');
                        });
                        buttons.close.addEventListener('click', () => window.location.reload());
                        MAE259B.render(data, options, { saveScreenshot, el$canvas, el$display, buttons });
                    });
                }
            });
        }
    });
};