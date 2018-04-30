MAE259B.initCamera = (el$canvas, el$resetBtn) => {
    const params = {
        h: 0,
        v: 0
    };

    let targetRotationOnMouseDownH = 0;
    let targetRotationOnMouseDownV = 0;

    let mouseXOnMouseDown = 0;
    let mouseYOnMouseDown = 0;

    const onMouseDown = event => {
        event.preventDefault();

        el$canvas.addEventListener('mousemove', onMouseMove, false);
        el$canvas.addEventListener('mouseup', onMouseUp, false);
        el$canvas.addEventListener('mouseout', onMouseUp, false);

        mouseXOnMouseDown = event.clientX;
        targetRotationOnMouseDownH = params.h;
        mouseYOnMouseDown = event.clientY;
        targetRotationOnMouseDownV = params.v;
    };

    const onMouseMove = event => {
        const mouseX = event.clientX;
        params.h = targetRotationOnMouseDownH + (mouseX - mouseXOnMouseDown) * 0.02;
        const mouseY = event.clientY;
        params.v = targetRotationOnMouseDownV + (mouseY - mouseYOnMouseDown) * 0.01;
    };

    const onMouseUp = () => {
        el$canvas.removeEventListener('mousemove', onMouseMove, false);
        el$canvas.removeEventListener('mouseup', onMouseUp, false);
        el$canvas.removeEventListener('mouseout', onMouseUp, false);
    };

    el$canvas.addEventListener('mousedown', onMouseDown, false);

    el$resetBtn.addEventListener('click', () => {
        params.h = 0;
        params.v = 0;
    });

    return params;
};