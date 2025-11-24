const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const img = document.getElementById('video-stream');
const spaces = [];
let drawing = false;
let startX, startY;
let referenceFrame = null;
let scaleX = 1;
let scaleY = 1;
let offsetX = 0;
let offsetY = 0;

function updateCanvasSize() {
    const rect = img.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    
    const imgRatio = img.naturalWidth / img.naturalHeight;
    const containerRatio = rect.width / rect.height;
    
    if (containerRatio > imgRatio) {
        const displayHeight = rect.height;
        const displayWidth = displayHeight * imgRatio;
        offsetX = (rect.width - displayWidth) / 2;
        offsetY = 0;
        scaleX = img.naturalWidth / displayWidth;
        scaleY = img.naturalHeight / displayHeight;
    } else {
        const displayWidth = rect.width;
        const displayHeight = displayWidth / imgRatio;
        offsetX = 0;
        offsetY = (rect.height - displayHeight) / 2;
        scaleX = img.naturalWidth / displayWidth;
        scaleY = img.naturalHeight / displayHeight;
    }
    
    redraw();
}

img.addEventListener('load', () => setTimeout(updateCanvasSize, 100));
window.addEventListener('resize', updateCanvasSize);

canvas.addEventListener('mousedown', (e) => {
    const rect = canvas.getBoundingClientRect();
    startX = e.clientX - rect.left - offsetX;
    startY = e.clientY - rect.top - offsetY;
    drawing = true;
});

canvas.addEventListener('mousemove', (e) => {
    if (!drawing) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left - offsetX;
    const y = e.clientY - rect.top - offsetY;
    
    redraw();
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    ctx.strokeRect(startX + offsetX, startY + offsetY, x - startX, y - startY);
});

canvas.addEventListener('mouseup', (e) => {
    if (!drawing) return;
    drawing = false;
    
    const rect = canvas.getBoundingClientRect();
    const endX = e.clientX - rect.left - offsetX;
    const endY = e.clientY - rect.top - offsetY;
    
    const w = endX - startX;
    const h = endY - startY;
    
    if (Math.abs(w) > 20 && Math.abs(h) > 20) {
        spaces.push({
            number: spaces.length + 1,
            x: Math.round(Math.min(startX, endX) * scaleX),
            y: Math.round(Math.min(startY, endY) * scaleY),
            w: Math.round(Math.abs(w) * scaleX),
            h: Math.round(Math.abs(h) * scaleY)
        });
        redraw();
        updateCount();
    }
});

function redraw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    spaces.forEach(space => {
        const displayX = space.x / scaleX + offsetX;
        const displayY = space.y / scaleY + offsetY;
        const displayW = space.w / scaleX;
        const displayH = space.h / scaleY;
        
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 2;
        ctx.strokeRect(displayX, displayY, displayW, displayH);
        ctx.fillStyle = '#00ff00';
        ctx.font = '16px Arial';
        ctx.fillText(`${space.number}`, displayX + 5, displayY + 20);
    });
}

function updateCount() {
    document.getElementById('space-count').textContent = spaces.length;
}

function captureReference() {
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = img.naturalWidth;
    tempCanvas.height = img.naturalHeight;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(img, 0, 0);
    referenceFrame = tempCanvas.toDataURL('image/jpeg');
    
    img.style.display = 'none';
    const frozenImg = document.createElement('img');
    frozenImg.id = 'frozen-frame';
    frozenImg.src = referenceFrame;
    frozenImg.style.width = '100%';
    frozenImg.style.height = '100%';
    frozenImg.style.objectFit = 'contain';
    img.parentElement.insertBefore(frozenImg, img);
    
    document.getElementById('reference-status').textContent = 'Referencia capturada';
    document.getElementById('save-btn').disabled = false;
}

function saveCalibration() {
    if (spaces.length === 0 || !referenceFrame) return;
    
    fetch(window.calibrateSaveUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            spaces: spaces,
            reference_frame: referenceFrame
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) window.location.href = window.dashboardUrl;
    });
}
